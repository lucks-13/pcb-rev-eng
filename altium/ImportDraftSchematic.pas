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
                R