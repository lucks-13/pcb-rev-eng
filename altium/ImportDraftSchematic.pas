Function TrimStr(Const S : String) : String;
Begin
    Result := Trim(S);
End;
Function SplitCSVLine(Const Line : String; OutFields : TStringList) 