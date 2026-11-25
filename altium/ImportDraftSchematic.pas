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
    For 