---
title: "[转]一个 CSS3 的自定义滚动条"
date: "2014-12-26 00:00:00"
updated: "2014-12-26 00:00:00"
tags:
-  CSS3
-  滚动条
---


转载一个 css3 的自定义滚动条~

[](/notename/ "archive 20141226")

```css
::-webkit-scrollbar {
    height:11px;
    width:11px
}
::-webkit-scrollbar-button {
    height:0;
    width:0
}
::-webkit-scrollbar-button:start:decrement,::-webkit-scrollbar-button:end:increment {
    display:block
}
::-webkit-scrollbar-button:vertical:start:increment,::-webkit-scrollbar-button:vertical:end:decrement {
    display:none
}
::-webkit-scrollbar-track:vertical,::-webkit-scrollbar-track:horizontal,::-webkit-scrollbar-thumb:vertical,::-webkit-scrollbar-thumb:horizontal,::-webkit-scrollbar-track:vertical,::-webkit-scrollbar-track:horizontal,::-webkit-scrollbar-thumb:vertical,::-webkit-scrollbar-thumb:horizontal {
    border-style:solid;
    border-color:transparent
}
::-webkit-scrollbar-track:vertical::-webkit-scrollbar-track:horizontal{
    background-clip:padding-box;
    background-color:#fff;
}
::-webkit-scrollbar-thumb {
    -webkit-box-shadow:inset 1px 1px 0 rgba(0,0,0,.1),inset 0 -1px 0 rgba(0,0,0,.07);
    background-clip:padding-box;
    background-color:rgba(0,0,0,.2);
    min-height:28px;
    padding-top:100
}
::-webkit-scrollbar-thumb:hover {
    -webkit-box-shadow:inset 1px 1px 1px rgba(0,0,0,.25);
    background-color:rgba(0,0,0,.4)
}
::-webkit-scrollbar-thumb:active {
    -webkit-box-shadow:inset 1px 1px 3px rgba(0,0,0,.35);
    background-color:rgba(0,0,0,.5)
}
::-webkit-scrollbar-track:vertical,::-webkit-scrollbar-track:horizontal,::-webkit-scrollbar-thumb:vertical,::-webkit-scrollbar-thumb:horizontal {
    border-width:0;
}
::-webkit-scrollbar-track:hover {
    -webkit-box-shadow:inset 1px 0 0 rgba(0,0,0,.1);
    background-color:rgba(0,0,0,.05)
}
::-webkit-scrollbar-track:active {
    -webkit-box-shadow:inset 1px 0 0 rgba(0,0,0,.14),inset -1px -1px 0 rgba(0,0,0,.07);
    background-color:rgba(0,0,0,.05)
}
```


