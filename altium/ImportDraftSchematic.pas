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
                RowDes := Fields[1];
                RowPin := Fields[2];
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

Procedure PlaceNetLabelNear(SchDoc : Isch_Document; X; Y : TCoord; Const NetName : String);
Var
    NetName : Isch_NetLabel;
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
    SchDoc : Isch_Document;
    BomLines, NetLines, Fields : TStringList;
    BomPath, NetPath : String;
    I, ColIdx, RowIdx : Integer;
    Desig, PartType, PartVal, Footprint : String;
    BaseX, B
