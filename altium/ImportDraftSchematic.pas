Function TrimStr(Const S : String) : String;
Begin
  Result := Trim(S);
End;

Function SplitCSVLine(Const Line : String; OutFields : TStringList) : Integer;
Var
  I, Len : Integer;
  InQuotes : Boolean;
  Cur : String;
  Ch : Char;
Begin
  OutFields.Clear;
  Cur := '';
  InQuotes := False;
  Len := Length(Line);
  For I := 1 To Len Do
  Begin
    Ch := Line[I];
    If Ch = '"' Then
      InQuotes := Not InQuotes
    Else If (Ch = ',') And (Not InQuotes) Then
    Begin
      OutFields.Add(TrimStr(Cur));
      Cur := '';
    End
    Else
      Cur := Cur + Ch;
  End;
  OutFields.Add(TrimStr(Cur));
  Result := OutFields.Count;
End;

Function FindNetForPin(NetLines : TStringList; Const Desig, PinNum : String) : String;
Var
  Idx : Integer;
  Fields : TStringList;
  NetName, RowDes, RowPin : String;
Begin
  Result := '';
  Fields := TStringList.Create;
  Try
    For Idx := 1 To NetLines.Count - 1 Do
    Begin
      If TrimStr(NetLines[Idx]) = '' Then Continue;
      SplitCSVLine(NetLines[Idx], Fields);
      If Fields.Count >= 3 Then
      Begin
        NetName := Fields[0];
        RowDes  := Fields[1];
        RowPin  := Fields[2];
        If SameText(RowDes, Desig) And SameText(RowPin, PinNum) Then
        Begin
          Result := NetName;
          Exit;
        End;
      End;
    End;
  Finally
    Fields.Free;
  End;
End;

Procedure PlaceNetLabelNear(SchDoc : ISch_Document; X, Y : TCoord; Const NetName : String);
Var
  NetLbl : ISch_NetLabel;
Begin
  If NetName = '' Then Exit;
  NetLbl := SchServer.SchObjectFactory(eNetLabel, eCreate_Default);
  If NetLbl = Nil Then Exit;
  NetLbl.Text := NetName;
  NetLbl.Location := Point(X, Y);
  SchDoc.RegisterSchObjectInContainer(NetLbl);
End;

Procedure ImportDraftFromFolder(Const FolderPath : String);
Var
  SchDoc : ISch_Document;
  BtmLines, NetLines, Fields : TStringList;
  BtmPath, NetPath : String;
  I, ColIdx, RowIdx : Integer;
  Desig, PartType, PartVal, Footprint : String;
  BaseX, BaseY, StepX, StepY, CurX, CurY : TCoord;
  Comp : ISch_Component;
  Iter : ISch_Iterator;
  PinObj : ISch_Pin;
  NetName : String;
Begin
  If SchServer = Nil Then
  Begin
    ShowMessage('Schematic server is not active.');
    Exit;
  End;

  SchDoc := SchServer.GetCurrentSchDocument;
  If (SchDoc = Nil) Or (SchDoc.ObjectId <> eSchematic) Then
  Begin
    ShowMessage('Please open a Schematic (.SchDoc) document first.');
    Exit;
  End;

  BtmPath := IncludeTrailingPathDelimiter(FolderPath) + 'bottom.csv';
  NetPath := IncludeTrailingPathDelimiter(FolderPath) + 'netlist.csv';

  If (Not FileExists(BtmPath)) Or (Not FileExists(NetPath)) Then
  Begin
    ShowMessage('Could not find bottom.csv or netlist.csv in: ' + FolderPath);
    Exit;
  End;

  BtmLines := TStringList.Create;
  NetLines := TStringList.Create;
  Fields   := TStringList.Create;
  Try
    BtmLines.LoadFromFile(BtmPath);
    NetLines.LoadFromFile(NetPath);

    BaseX := MilsToCoord(1000);
    BaseY := MilsToCoord(7000);
    StepX := MilsToCoord(1800);
    StepY := MilsToCoord(1600);

    SchServer.ProcessControl.PreProcess(SchDoc, '');
    Try
      ColIdx := 0;
      RowIdx := 0;

      For I := 1 To BtmLines.Count - 1 Do
      Begin
        If TrimStr(BtmLines[I]) = '' Then Continue;
        SplitCSVLine(BtmLines[I], Fields);
        If Fields.Count < 4 Then Continue;

        Desig     := Fields[0];
        PartType  := Fields[1];
        PartVal   := Fields[2];
        Footprint := Fields[3];

        CurX := BaseX + (ColIdx * StepX);
        CurY := BaseY - (RowIdx * StepY);

        Comp := SchServer.SchObjectFactory(eSchComponent, eCreate_Default);
        If Comp <> Nil Then
        Begin
          Comp.Designator.Text := Desig;
          Comp.Comment.Text    := PartVal;
          Comp.Footprint       := Footprint;
          Comp.Location        := Point(CurX, CurY);
          SchDoc.RegisterSchObjectInContainer(Comp);

          Iter := Comp.SchIteratorFactory;
          If Iter <> Nil Then
          Begin
            Iter.AddFilter_ObjectSet(MkSet(ePin));
            PinObj := Iter.FirstSchObject;
            While PinObj <> Nil Do
            Begin
              NetName := FindNetForPin(NetLines, Desig, PinObj.Designator);
              PlaceNetLabelNear(SchDoc, PinObj.Location.X, PinObj.Location.Y, NetName);
              PinObj := Iter.NextSchObject;
            End;
            Comp.SchIteratorDestroy(Iter);
          End;
        End;

        Inc(ColIdx);
        If ColIdx >= 5 Then
        Begin
          ColIdx := 0;
          Inc(RowIdx);
        End;
      End;
    Finally
      SchServer.ProcessControl.PostProcess(SchDoc, '');
    End;

    SchDoc.GraphicallyInvalidate;
    ShowMessage('Draft schematic import complete.');
  Finally
    Fields.Free;
    NetLines.Free;
    BtmLines.Free;
  End;
End;

Procedure RunImport;
Var
  FolderPath : String;
Begin
  FolderPath := 'D:\Hack Club\pcb-rev-eng\outputs\sample_board';
  ImportDraftFromFolder(FolderPath);
End;