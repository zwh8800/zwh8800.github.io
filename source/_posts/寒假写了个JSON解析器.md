---
title: "寒假写了个 JSON 解析器"
date: "2015-05-26 00:00:00"
updated: "2015-05-26 00:00:00"
tags:
-  JSON
-  解析器
---


一个 JSON 解析器

[](/notename/ "archive 20150526")

使用方法:
```
string data = File.ReadAllText(@"f:\1.Json");
dynamic obj = Json.Parse(data);
 
Console.WriteLine(obj.employees[0].firstName);
 
foreach (var it in obj.employees)
{
    Console.WriteLine(it.lastName);
}
```

假设 json 文件如下:
```JSON
{
    "employees": [
        {
            "firstName": "Bill",
            "lastName": "Gates"
        },
        {
            "firstName": "George",
            "lastName": "Bush"
        },
        {
            "firstName": "Thomas",
            "lastName": "Carter"
        }
    ]
}
```

使用了 c#4.0 的动态特性, c# 越来越像动态语言了, 用着真舒服.
代码如下, 就是个递归下降:
```
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Dynamic;
 
namespace Json
{
    public class Json
    {
        private class JsonObject : DynamicObject
        {
            public JsonObject(Dictionary<string, dynamic> member)
            {
                this.member = member;
            }
 
            public override bool TryGetMember(GetMemberBinder binder, out object result)
            {
                if (member.ContainsKey(binder.Name))
                {
                    result = member[binder.Name];
                    return true;
                }
                else
                {
                    result = null;
                    return false;
                }
            }
 
            private Dictionary<string, dynamic> member;
        }
 
        private static int CharToInt(char c)
        {
            switch (c)
            {
                case '0':
                    return 0;
                case '1':
                    return 1;
                case '2':
                    return 2;
                case '3':
                    return 3;
                case '4':
                    return 4;
                case '5':
                    return 5;
                case '6':
                    return 6;
                case '7':
                    return 7;
                case '8':
                    return 8;
                case '9':
                    return 9;
            }
            throw new Exception("c不是一个数字字符");
        }
 
        private enum TokenType
        {
            LBrace, RBrace,
            LBracket, RBracket,
            Colon, Comma,
            True, False,
            Null, String,
            Number
        }
 
        private struct Token
        {
            public TokenType type;
            public dynamic value;
        }
 
        private enum NumberState
        {
            Start, MinusRead, ZeroRead, InInt, DotRead, InFraction, ERead, InExponent, End
        }
 
        private static Token GetToken(string json, ref int i)
        {
            while (i < json.Length && char.IsWhiteSpace(json[i]))
                i++;
 
            Token token = new Token();
            string sub = json.Substring(i);
 
            if (json[i] == '{')
            {
                token.type = TokenType.LBrace;
                i = i + 1;
            }
            else if (json[i] == '}')
            {
                token.type = TokenType.RBrace;
                i = i + 1;
            }
            else if (json[i] == '[')
            {
                token.type = TokenType.LBracket;
                i = i + 1;
            }
            else if (json[i] == ']')
            {
                token.type = TokenType.RBracket;
                i = i + 1;
            }
            else if (json[i] == ':')
            {
                token.type = TokenType.Colon;
                i = i + 1;
            }
            else if (json[i] == ',')
            {
                token.type = TokenType.Comma;
                i = i + 1;
            }
            else if (sub.StartsWith("true"))
            {
                token.type = TokenType.True;
                i = i + 4;
            }
            else if (sub.StartsWith("false"))
            {
                token.type = TokenType.False;
                i = i + 4;
            }
            else if (sub.StartsWith("null"))
            {
                token.type = TokenType.Null;
                i = i + 4;
            }
            else if (json[i] == '"')        //string
            {
                StringBuilder sb = new StringBuilder();
                i++;
 
                while (i < json.Length)
                {
                    int len = 0;
                    while (i + len < json.Length && json[i + len] != '"' && json[i + len] != '\\')
                        len++;
 
                    sb.Append(json.Substring(i, len));
 
                    if (i + len >= json.Length)
                    {
                        throw new Exception("未找到匹配的引号");
                    }
                    else if (json[i + len] == '"')
                    {
                        i += len + 1;
                        break;
                    }
 
                    i += len + 1;
                    switch (json[i])
                    {
                        case '"':
                            sb.Append('"');
                            i++;
                            break;
                        case '\\':
                            sb.Append('\\');
                            i++;
                            break;
                        case '/':
                            sb.Append('/');
                            i++;
                            break;
                        case 'b':
                            sb.Append('\b');
                            i++;
                            break;
                        case 'f':
                            sb.Append('\f');
                            i++;
                            break;
                        case 'n':
                            sb.Append('\n');
                            i++;
                            break;
                        case 'r':
                            sb.Append('\r');
                            i++;
                            break;
                        case 't':
                            sb.Append('\t');
                            i++;
                            break;
                        case 'u':
                            string hex = json.Substring(i + 1, 4);
                            ushort code = Convert.ToUInt16(hex, 16);
                            char c = (char)code;
                            sb.Append(c);
                            i += 5;
                            break;
                    }
                }
 
                token.value = sb.ToString();
                token.type = TokenType.String;
            }
            else if (json[i] == '-' || char.IsNumber(json[i]))    //nubmer
            {
                dynamic value = 0;
                bool isMinus = false;
                int frac = 10;
                bool isExponentNegative = false;
                int exponent = 0;
 
                NumberState state = NumberState.Start;
 
                while (state != NumberState.End)
                {
                    switch (state)
                    {
                        case NumberState.Start:
                            if (json[i] == '-')
                            {
                                isMinus = true;
 
                                state = NumberState.MinusRead;
                            }
                            else if (json[i] == '0')
                            {
                                state = NumberState.ZeroRead;
                            }
                            else if (char.IsNumber(json[i]))
                            {
                                value = CharToInt(json[i]);
                                state = NumberState.InInt;
                            }
                            else
                            {
                                throw new Exception("不能识别的字符‘" + json[i] + "’");
                            }
                            i++;
                            break;
                        case NumberState.MinusRead:
                            if (json[i] == '0')
                            {
                                state = NumberState.ZeroRead;
                            }
                            else if (char.IsNumber(json[i]))
                            {
                                value = CharToInt(json[i]);
                                state = NumberState.InInt;
                            }
                            else
                            {
                                throw new Exception("不能识别的字符‘" + json[i] + "’");
                            }
                            i++;
                            break;
                        case NumberState.InInt:
                            if (char.IsNumber(json[i]))
                            {
                                value *= 10;
                                value += CharToInt(json[i]);
                            }
                            else if (json[i] == '.')
                            {
                                state = NumberState.DotRead;
                            }
                            else if (json[i] == 'e' || json[i] == 'E')
                            {
                                state = NumberState.ERead;
                            }
                            else
                            {
                                i--;
                                state = NumberState.End;
                            }
                            i++;
                            break;
                        case NumberState.ZeroRead:
                            if (json[i] == '.')
                            {
                                state = NumberState.DotRead;
                            }
                            else if (json[i] == 'e' || json[i] == 'E')
                            {
                                state = NumberState.ERead;
                            }
                            else
                            {
                                i--;
                                state = NumberState.End;
                            }
                            i++;
                            break;
                        case NumberState.DotRead:
                            if (char.IsNumber(json[i]))
                            {
                                value += (double)CharToInt(json[i]) / frac;
                                frac *= 10;
                                state = NumberState.InFraction;
                            }
                            else
                            {
                                throw new Exception("不能识别的字符‘" + json[i] + "’");
                            }
                            i++;
                            break;
                        case NumberState.InFraction:
                            if (char.IsNumber(json[i]))
                            {
                                value += (double)CharToInt(json[i]) / frac;
                                frac *= 10;
                            }
                            else if (json[i] == 'e' || json[i] == 'E')
                            {
                                state = NumberState.ERead;
                            }
                            else
                            {
                                i--;
                                state = NumberState.End;
                            }
                            i++;
                            break;
                        case NumberState.ERead:
                            if (char.IsNumber(json[i]))
                            {
                                exponent = CharToInt(json[i]);
                                state = NumberState.InExponent;
                            }
                            else if (json[i] == '+')
                            {
                                state = NumberState.InExponent;
                            }
                            else if (json[i] == '-')
                            {
                                isExponentNegative = true;
                                state = NumberState.InExponent;
                            }
                            else
                            {
                                throw new Exception("不能识别的字符‘" + json[i] + "’");
                            }
                            i++;
                            break;
                        case NumberState.InExponent:
                            if (char.IsNumber(json[i]))
                            {
                                exponent *= 10;
                                exponent = CharToInt(json[i]);
                            }
                            else
                            {
                                i--;
                                state = NumberState.End;
                            }
                            i++;
                            break;
                    }
                    if (i >= json.Length)
                        state = NumberState.End;
                }
 
                if (exponent != 0)
                {
                    if (isExponentNegative)
                    {
                        value = value * Math.Pow(10, -exponent);
                    }
                    else
                    {
                        value = value * Math.Pow(10, exponent);
                    }
                }
                if (isMinus)
                    token.value = -value;
                else
                    token.value = value;
                token.type = TokenType.Number;
 
            }
            else
                throw new Exception("不能识别的字符‘" + json[i] + "’");
 
            while (i < json.Length && char.IsWhiteSpace(json[i]))
                i++;
            return token;
        }
 
        private static dynamic Value(string json, ref int i)
        {
            Token token = GetToken(json, ref i);
            if (token.type == TokenType.Null)
                return null;
            else if (token.type == TokenType.False)
                return false;
            else if (token.type == TokenType.True)
                return true;
            else if (token.type == TokenType.Number)
                return token.value;
            else if (token.type == TokenType.String)
                return token.value;
            else if (token.type == TokenType.LBrace)
            {
                Dictionary<string, dynamic> member = new Dictionary<string, dynamic>();
 
                bool first = true;
                while (true)
                {
                    if (first)
                    {
                        int tmpi = i;
                        token = GetToken(json, ref i);
                        if (token.type == TokenType.RBrace)
                            break;
                        else
                            i = tmpi;
 
                        first = false;
                    }
 
                    token = GetToken(json, ref i);
                    if (token.type != TokenType.String)
                    {
                        throw new Exception("出乎意料的Token: " + token.type);
                    }
                    string name = token.value;
 
                    token = GetToken(json, ref i);
                    if (token.type != TokenType.Colon)
                    {
                        throw new Exception("出乎意料的Token: " + token.type);
                    }
 
                    dynamic val = Value(json, ref i);
                    member[name] = val;
 
                    token = GetToken(json, ref i);
                    if (token.type == TokenType.Comma)
                        continue;
                    else if (token.type == TokenType.RBrace)
                        break;
                    else
                        throw new Exception("出乎意料的Token: " + token.type);
                }
 
                return new JsonObject(member);
            }
            else if (token.type == TokenType.LBracket)
            {
                List<dynamic> list = new List<dynamic>();
                bool first = true;
                while (true)
                {
                    if (first)
                    {
                        int tmpi = i;
                        token = GetToken(json, ref i);
                        if (token.type == TokenType.RBracket)
                            break;
                        else
                            i = tmpi;
 
                        first = false;
                    }
 
                    list.Add(Value(json, ref i));
                    token = GetToken(json, ref i);
                    if (token.type == TokenType.Comma)
                        continue;
                    else if (token.type == TokenType.RBracket)
                        break;
                    else
                        throw new Exception("出乎意料的Token: " + token.type);
                }
                return list.ToArray();
            }
            else
            {
                throw new Exception("出乎意料的Token: " + token.type);
            }
        }
 
        public static dynamic Parse(string json)
        {
            int i = 0;
            return Value(json, ref i);
        }
    }
}
```


