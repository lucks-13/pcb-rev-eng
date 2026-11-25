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

Function FinD