include("../Data/Script/Common/include.lua")

local scroll_bg = nil
local CurVoicePackIndex = 1
local check_list = {}
local check_pattern = {}

local imgSoundProgress = nil
local imgMusicProgress = nil
local MAXVALUE = 100

local AA = nil
local BB = nil
local CC = nil
local DD = nil
local EE = nil
local FF = nil

local AWnd = nil
local BWnd = nil
local CWnd = nil
local DWnd = nil
local EWnd = nil
local FWnd = nil

local AP = nil
local BP = nil
local CP = nil
local FP = nil
local EP = nil
local DP = nil
local AP_FONT = 40
local BP_FONT = 60
local CP_FONT = 99
local FP_FONT = 120
local EP_FONT = 120
local DP_FONT = 120

local A1 = nil
local B1 = nil
local C1 = nil
local D1 = nil
local E1 = nil
local F1 = nil

local posx_move = -240
local posy_move = -150

-- 语音包选择
local VoicePack_BK = nil
local BTN_LIST = nil
local LIST_BK = nil
local Font_showAll = nil
local BTN_VoicePack = {}
local Font_VoicePack = {}
local BTN_VoicePackFont = {"默认", "默认", "默认", "默认", "默认", "默认", "默认", "默认", "默认",
                           "默认", "默认", "默认"}
local BTN_VoicePackId = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}

-- 鼠标皮肤
local MouseSkin_ButtonList = nil
local MouseSkin_ListBK = nil
local MouseSkin_FontShowAll = nil
local MouseSkin_FontList = {"null", "null", "null", "null", "null", "null", "null", "null"}
local MouseSkin_Button = {}
local MouseSkin_TextList = {}
local MouseSkin_SkinID = {}

local ChangeUI_ButtonList = nil
local ChangeUI_FontShowAll = nil
local ChangeUI_ListBK = nil
local ChangeUI_FontList = {"默认", "经典"}
local ChangeUI_Button = {}

-- 抗锯齿
local AntiAlias, AntiAliasFont, AntiAliasBK = nil, nil, nil
local AntiAliasFontItem = {"关闭", "2倍", "4倍", "8倍", "16倍"}
local AntiAliasListBK = {}
local AntiAliasListFont = {}
local index_AntiAlias = 0

-- 摄像机高度
local CameraZoom = nil
local CameraZoomBtn = nil
local CameraZoomMax = 35
local CameraZoomMin = 16

function InitSetup_GameUI(wnd, bisopen)
    g_setup_game_ui = CreateWindow(wnd.id, 0, 0, 1920, 1080)
    local BK = g_setup_game_ui:AddImage(path_lolshopbuy .. "shopbuybg.BMP", 18, 18, 783, 530)
    BK:SetImageFrameWidth(50)
    BK:AddFont("游戏设置", 18, 8, 0, 0, 783, 42, 0xffe684)
    InitMainSetup_GameA(g_setup_game_ui)
    InitMainSetup_Game(g_setup_game_ui)
    g_setup_game_ui:SetVisible(bisopen)
end

function InitMainSetup_Game(wnd)
    -- local BK = wnd:AddImage(path_lolshopbuy .. "shopbuybg.BMP", 18, 18, 783, 476)
    -- BK:SetImageFrameWidth(50)
    -- BK:AddFont("游戏设置", 18, 8, 0, 0, 783, 42, 0xffe684)

    local btn_close = wnd:AddButton(path_lolcommon .. "close1.BMP", path_lolcommon .. "close2.BMP",
        path_lolcommon .. "close3.BMP", 1017 + posx_move, 156 + posy_move, 33, 34)
    btn_close.script[XE_LBUP] = function()
        XClickPlaySound(UI_click_new)
        Set_SetupIsVisible(0)
        XClickCancelButton_Set(1)
    end
    local btn_back = wnd:AddButton(path_lolcommon .. "cancel1.BMP", path_lolcommon .. "cancel2.BMP",
        path_lolcommon .. "cancel3.BMP", 290 + posx_move, 630 + posy_move, 166, 55)
    btn_back:AddFont("返回设置", 15, 8, 0, 0, 166, 55, 0xffffff)
    btn_back.script[XE_LBUP] = function()
        XClickPlaySound(UI_click_new)

        XClickCancelButton_Set(1)
        Set_SetupGameIsVisible(0)
    end
    local btn_apply = wnd:AddButton(path_lolcommon .. "cancel1.BMP", path_lolcommon .. "cancel2.BMP",
        path_lolcommon .. "cancel3.BMP", 840 + posx_move, 630 + posy_move, 166, 55)
    btn_apply:AddFont("确认", 15, 8, 0, 0, 166, 55, 0xffffff)
    btn_apply.script[XE_LBUP] = function()
        XClickPlaySound(UI_click_new)

        XClickConfirmButton_Set(1)
        Set_SetupGameIsVisible(0)
    end

    wnd:AddFont("功能设置", 18, 0, 312 + posx_move, 387 + posy_move, 100, 20, 0xffffff)
    wnd:AddFont("游戏设置", 18, 0, 708 + posx_move, 222 + posy_move, 100, 20, 0xffffff)
    wnd:AddFont("音效设置", 18, 0, 312 + posx_move, 222 + posy_move, 100, 20, 0xffffff)
    wnd:AddFont("音效", 15, 0, 328 + posx_move, 253 + posy_move, 100, 20, 0x8580d2)
    wnd:AddFont("音乐", 15, 0, 328 + posx_move, 281 + posy_move, 100, 20, 0x8580d2)
    wnd:AddFont("声音", 15, 0, 329 + posx_move, 309 + posy_move, 100, 20, 0x8580d2)
    wnd:AddFont("系统", 15, 0, 327 + posx_move, 338 + posy_move, 100, 20, 0x8580d2)
    wnd:AddFont("小地图", 15, 0, 724 + posx_move, 253 + posy_move, 100, 20, 0x8580d2)
    wnd:AddFont("滚屏速度", 15, 0, 724 + posx_move, 282 + posy_move, 100, 20, 0x8580d2)
    wnd:AddFont("语音包", 15, 0, 724 + posx_move, 309 + posy_move, 100, 20, 0x8580d2)
    wnd:AddFont("鼠标皮肤", 15, 0, 724 + posx_move, 337 + posy_move, 100, 20, 0x8580d2)

    -- 滑动条
    imgSoundProgress = wnd:AddImage(path_setup .. "dragBK1_setup_2.BMP", 389 + posx_move, 256 + posy_move, 150, 14)
    imgMusicProgress = wnd:AddImage(path_setup .. "dragBK1_setup_2.BMP", 389 + posx_move, 285 + posy_move, 150, 14)
    wnd:AddImage(path_setup .. "dragBK1_setup_2.BMP", 389 + posx_move, 312 + posy_move, 150, 14)
    wnd:AddImage(path_setup .. "dragBK1_setup_2.BMP", 389 + posx_move, 341 + posy_move, 150, 14)
    wnd:AddImage(path_setup .. "dragBK1_setup_2.BMP", 817 + posx_move, 256 + posy_move, 150, 14)
    wnd:AddImage(path_setup .. "dragBK1_setup_2.BMP", 817 + posx_move, 285 + posy_move, 150, 14)

    AA = wnd:AddImage(path_setup .. "dragBK2_setup_2.BMP", 392 + posx_move, 258 + posy_move, 145, 10)
    BB = wnd:AddImage(path_setup .. "dragBK2_setup_2.BMP", 392 + posx_move, 287 + posy_move, 145, 10)
    CC = wnd:AddImage(path_setup .. "dragBK2_setup_2.BMP", 392 + posx_move, 314 + posy_move, 145, 10)
    DD = wnd:AddImage(path_setup .. "dragBK2_setup_2.BMP", 392 + posx_move, 343 + posy_move, 145, 10)
    EE = wnd:AddImage(path_setup .. "dragBK2_setup_2.BMP", 820 + posx_move, 258 + posy_move, 145, 10)
    FF = wnd:AddImage(path_setup .. "dragBK2_setup_2.BMP", 820 + posx_move, 287 + posy_move, 145, 10)

    -- 所有的滑动条
    -- 音效
    local AAWnd = AA:AddImage(path_dv .. "R.BMP", 0, 0, 150, 20)
    AAWnd:SetTransparent(0)
    AAWnd.script[XE_LBUP] = function()
        local X, Y = AA:GetPosition()
        local L = XGetCursorPosX() - X
        L = math.max(0, L)
        L = math.min(L, 125)

        local tempnum = 0
        if g_setup_game_ui:IsVisible() then
            tempnum = 1
        end
        AP_FONT = string.format("%d", (L / 125) * MAXVALUE)
        XUpDateSoundScrollBarPos_Tab(tempnum, AP_FONT)
        XSetAddImageRect(AA.id, 0, 0, L + 10, 10, 392 + posx_move, 258 + posy_move, L + 10, 10)
        AP:SetFontText(AP_FONT .. "%", 0xffffff)
        A1._L = L
        A1:SetPosition(A1._L, 0)
    end
    AWnd = CreateWindow(AA.id, -3, -6, 28, 22)
    AWnd:SetTouchEnabled(0)
    A1 = AWnd:AddButton(path_setup .. "dragBtn_setup_2.BMP", path_setup .. "dragBtn_setup_2.BMP",
        path_setup .. "dragBtn_setup_2.BMP", 0, 0, 28, 22)
    XSetWindowFlag(A1.id, 1, 2, 0, 125)

    A1:ToggleBehaviour(XE_ONUPDATE, 1)
    A1:ToggleEvent(XE_ONUPDATE, 1)

    A1.script[XE_ONUPDATE] = function()
        if A1._L == nil then
            A1._L = 0
        end
        local L, T, R, B = XGetWindowClientPosition(A1.id)
        if A1._L ~= L then
            local tempnum = 0
            if g_setup_game_ui:IsVisible() then
                tempnum = 1
            end
            AP_FONT = string.format("%d", (L / 125) * MAXVALUE)
            XUpDateSoundScrollBarPos_Tab(tempnum, AP_FONT)
            XSetAddImageRect(AA.id, 0, 0, L + 10, 10, 392 + posx_move, 258 + posy_move, L + 10, 10)
            AP:SetFontText(AP_FONT .. "%", 0xffffff)
            A1._L = L
        end
    end

    -- 音乐
    local BBWnd = BB:AddImage(path_dv .. "R.BMP", 0, 0, 150, 20)
    BBWnd:SetTransparent(0)
    BBWnd.script[XE_LBUP] = function()
        local X, Y = BB:GetPosition()
        local L = XGetCursorPosX() - X
        L = math.max(0, L)
        L = math.min(L, 125)

        local tempnum = 0
        if g_setup_game_ui:IsVisible() then
            tempnum = 1
        end
        BP_FONT = string.format("%d", (L / 125) * MAXVALUE)
        XUpDateMusicScrollBarPos_Tab(tempnum, BP_FONT)
        BB:SetAddImageRect(BB.id, 0, 0, L + 10, 10, 392 + posx_move, 287 + posy_move, L + 10, 10)
        BP:SetFontText(BP_FONT .. "%", 0xffffff)
        B1._L = L
        B1:SetPosition(B1._L, 0)
    end
    BWnd = CreateWindow(BB.id, -3, -6, 28, 22)
    BWnd:SetTouchEnabled(0)
    B1 = BWnd:AddButton(path_setup .. "dragBtn_setup_2.BMP", path_setup .. "dragBtn_setup_2.BMP",
        path_setup .. "dragBtn_setup_2.BMP", 0, 0, 28, 22)
    XSetWindowFlag(B1.id, 1, 2, 0, 125)

    B1:ToggleBehaviour(XE_ONUPDATE, 1)
    B1:ToggleEvent(XE_ONUPDATE, 1)

    B1.script[XE_ONUPDATE] = function()
        if B1._L == nil then
            B1._L = 0
        end
        local L, T, R, B = XGetWindowClientPosition(B1.id)
        if B1._L ~= L then
            local tempnum = 0
            if g_setup_game_ui:IsVisible() then
                tempnum = 1
            end
            BP_FONT = string.format("%d", (L / 125) * MAXVALUE)
            XUpDateMusicScrollBarPos_Tab(tempnum, BP_FONT)
            BB:SetAddImageRect(BB.id, 0, 0, L + 10, 10, 392 + posx_move, 287 + posy_move, L + 10, 10)
            BP:SetFontText(BP_FONT .. "%", 0xffffff)
            B1._L = L
        end
    end

    ------------声音
    local CCWnd = CC:AddImage(path_dv .. "R.BMP", 0, 0, 150, 20)
    CCWnd:SetTransparent(0)
    CCWnd.script[XE_LBUP] = function()
        local X, Y = CC:GetPosition()
        local L = XGetCursorPosX() - X
        L = math.max(0, L)
        L = math.min(L, 125)

        local tempnum = 0
        if g_setup_game_ui:IsVisible() then
            tempnum = 1
        end
        CP_FONT = string.format("%d", (L / 125) * MAXVALUE)
        XUpDateSaidScrollBarPos_Tab(tempnum, CP_FONT)
        CC:SetAddImageRect(CC.id, 0, 0, L + 10, 10, 392 + posx_move, 314 + posy_move, L + 10, 10)
        CP:SetFontText(CP_FONT .. "%", 0xffffff)
        C1._L = L
        C1:SetPosition(C1._L, 0)
    end

    CWnd = CreateWindow(CC.id, -3, -6, 28, 22)
    CWnd:SetTouchEnabled(0)
    C1 = CWnd:AddButton(path_setup .. "dragBtn_setup_2.BMP", path_setup .. "dragBtn_setup_2.BMP",
        path_setup .. "dragBtn_setup_2.BMP", 0, 0, 28, 22)
    XSetWindowFlag(C1.id, 1, 2, 0, 125)

    C1:ToggleBehaviour(XE_ONUPDATE, 1)
    C1:ToggleEvent(XE_ONUPDATE, 1)

    C1.script[XE_ONUPDATE] = function()
        if C1._L == nil then
            C1._L = 0
        end
        local L, T, R, B = XGetWindowClientPosition(C1.id)
        if C1._L ~= L then
            local tempnum = 0
            if g_setup_game_ui:IsVisible() then
                tempnum = 1
            end
            CP_FONT = string.format("%d", (L / 125) * MAXVALUE)
            XUpDateSaidScrollBarPos_Tab(tempnum, CP_FONT)
            CC:SetAddImageRect(CC.id, 0, 0, L + 10, 10, 392 + posx_move, 314 + posy_move, L + 10, 10)
            CP:SetFontText(CP_FONT .. "%", 0xffffff)
            C1._L = L
        end
    end
    ------------系统语音
    local FFWnd = FF:AddImage(path_dv .. "R.BMP", 0, 0, 150, 20)
    FFWnd:SetTransparent(0)
    FFWnd.script[XE_LBUP] = function()
        local X, Y = FF:GetPosition()
        local L = XGetCursorPosX() - X
        L = math.max(0, L)
        L = math.min(L, 125)

        local tempnum = 0
        if g_setup_game_ui:IsVisible() then
            tempnum = 1
        end
        FP_FONT = string.format("%d", (L / 125) * MAXVALUE)
        XUpDateVoiceScrollBarPos_Tab(tempnum, FP_FONT)
        FF:SetAddImageRect(FF.id, 0, 0, L + 10, 10, 392 + posx_move, 343 + posy_move, L + 10, 10)
        FP:SetFontText(FP_FONT .. "%", 0xffffff)
        F1._L = L
        F1:SetPosition(F1._L, 0)
    end

    FWnd = CreateWindow(FF.id, -3, -6, 28, 22)
    FWnd:SetTouchEnabled(0)
    F1 = FWnd:AddButton(path_setup .. "dragBtn_setup_2.BMP", path_setup .. "dragBtn_setup_2.BMP",
        path_setup .. "dragBtn_setup_2.BMP", 0, 0, 28, 22)
    XSetWindowFlag(F1.id, 1, 2, 0, 125)

    F1:ToggleBehaviour(XE_ONUPDATE, 1)
    F1:ToggleEvent(XE_ONUPDATE, 1)

    F1.script[XE_ONUPDATE] = function()
        if F1._L == nil then
            F1._L = 0
        end
        local L, T, R, B = XGetWindowClientPosition(F1.id)
        if F1._L ~= L then
            local tempnum = 0
            if g_setup_game_ui:IsVisible() then
                tempnum = 1
            end
            FP_FONT = string.format("%d", (L / 125) * MAXVALUE)
            XUpDateVoiceScrollBarPos_Tab(tempnum, FP_FONT)
            FF:SetAddImageRect(FF.id, 0, 0, L + 10, 10, 392 + posx_move, 343 + posy_move, L + 10, 10)
            FP:SetFontText(FP_FONT .. "%", 0xffffff)
            F1._L = L
        end
    end
    ------------小地图	
    local DDWnd = DD:AddImage(path_dv .. "R.BMP", 0, 0, 150, 20)
    DDWnd:SetTransparent(0)
    DDWnd.script[XE_LBUP] = function()
        local X, Y = DD:GetPosition()
        local L = XGetCursorPosX() - X
        L = math.max(0, L)
        L = math.min(L, 125)

        local tempnum = 0
        if g_setup_game_ui:IsVisible() then
            tempnum = 1
        end
        XUpDateMiniMapScrollBarPos_Tab(tempnum, L / 125 * 20)
        DD:SetAddImageRect(DD.id, 0, 0, L + 10, 10, 820 + posx_move, 258 + posy_move, L + 10, 10)
        D1._L = L
        D1:SetPosition(D1._L, 0)
    end

    DWnd = CreateWindow(DD.id, -3, -6, 28, 22)
    DWnd:SetTouchEnabled(0)
    D1 = DWnd:AddButton(path_setup .. "dragBtn_setup_2.BMP", path_setup .. "dragBtn_setup_2.BMP",
        path_setup .. "dragBtn_setup_2.BMP", 0, 0, 28, 22)
    XSetWindowFlag(D1.id, 1, 2, 0, 125)
    D1:ToggleBehaviour(XE_ONUPDATE, 1)
    D1:ToggleEvent(XE_ONUPDATE, 1)

    D1.script[XE_ONUPDATE] = function()
        if D1._L == nil then
            D1._L = 0
        end
        local L, T, R, B = XGetWindowClientPosition(D1.id)
        if D1._L ~= L then
            local tempnum = 0
            if g_setup_game_ui:IsVisible() then
                tempnum = 1
            end
            XUpDateMiniMapScrollBarPos_Tab(tempnum, L / 125 * MAXVALUE)
            DD:SetAddImageRect(DD.id, 0, 0, L + 10, 10, 820 + posx_move, 258 + posy_move, L + 10, 10)
            D1._L = L
        end
    end

    ------------滚屏速度
    local EEWnd = EE:AddImage(path_dv .. "R.BMP", 0, 0, 150, 20)
    EEWnd:SetTransparent(0)
    EEWnd.script[XE_LBUP] = function()
        local X, Y = EE:GetPosition()
        local L = XGetCursorPosX() - X
        L = math.max(0, L)
        L = math.min(L, 125)

        local tempnum = 0
        if g_setup_game_ui:IsVisible() then
            tempnum = 1
        end
        XUpDateScreenRollScrollBarPos_Tab(tempnum, L / 125 * 1000)
        EE:SetAddImageRect(EE.id, 0, 0, L + 10, 10, 820 + posx_move, 287 + posy_move, L + 10, 10)
        E1._L = L
        E1:SetPosition(E1._L, 0)
    end

    EWnd = CreateWindow(EE.id, -3, -6, 28, 22)
    EWnd:SetTouchEnabled(0)
    E1 = EWnd:AddButton(path_setup .. "dragBtn_setup_2.BMP", path_setup .. "dragBtn_setup_2.BMP",
        path_setup .. "dragBtn_setup_2.BMP", 0, 0, 28, 22)
    XSetWindowFlag(E1.id, 1, 2, 0, 125)

    E1:ToggleBehaviour(XE_ONUPDATE, 1)
    E1:ToggleEvent(XE_ONUPDATE, 1)

    E1.script[XE_ONUPDATE] = function()
        if E1._L == nil then
            E1._L = 0
        end
        local L, T, R, B = XGetWindowClientPosition(E1.id)
        if E1._L ~= L then
            local tempnum = 0
            if g_setup_game_ui:IsVisible() then
                tempnum = 1
            end
            XUpDateScreenRollScrollBarPos_Tab(tempnum, L / 125 * 1000)
            EE:SetAddImageRect(EE.id, 0, 0, L + 10, 10, 820 + posx_move, 287 + posy_move, L + 10, 10)
            E1._L = L
        end
    end
    ---------音乐百分比
    AP = wnd:AddFont(AP_FONT .. "%", 15, 0, 546 + posx_move, 256 + posy_move, 200, 20, 0xffffff)
    BP = wnd:AddFont(BP_FONT .. "%", 15, 0, 546 + posx_move, 285 + posy_move, 200, 20, 0xffffff)
    CP = wnd:AddFont(CP_FONT .. "%", 15, 0, 546 + posx_move, 312 + posy_move, 200, 20, 0xffffff)
    FP = wnd:AddFont(FP_FONT .. "%", 15, 0, 546 + posx_move, 341 + posy_move, 200, 20, 0xffffff)
    EP = wnd:AddFont(EP_FONT .. "%", 15, 0, 974 + posx_move, 285 + posy_move, 200, 20, 0xffffff)
    DP = wnd:AddFont(DP_FONT .. "%", 15, 0, 974 + posx_move, 256 + posy_move, 200, 20, 0xffffff)
    EP:SetVisible(0)
    DP:SetVisible(0)

    -- 界面切换
    ChangeUI_ButtonList = wnd:AddTwoButton(path_setup .. "btn1_voice_2.BMP", path_setup .. "btn2_voice_2.BMP",
        path_setup .. "btn1_voice_2.BMP", 796 + posx_move, 365 + posy_move, 177, 21)
    ChangeUI_FontShowAll = ChangeUI_ButtonList:AddFont("默认", 12, 0, 8, 2, 145, 20, 0xf9c569)

    ChangeUI_ButtonList:SetVisible(0)
    ChangeUI_ListBK = wnd:AddImage(path_setup .. "voice_bg_2.BMP", 806 + posx_move, 385 + posy_move, 152, 202)
    ChangeUI_ListBK:SetImageFrameWidth(10)
    ChangeUI_ListBK:SetVisible(0)

    for dis = 1, #ChangeUI_FontList do
        ChangeUI_Button[dis] = wnd:AddImage(path_setup .. "voice_select_2.BMP", 806 + posx_move,
            357 + posy_move + dis * 29, 150, 20)
        ChangeUI_ListBK:AddFont(ChangeUI_FontList[dis], 12, 0, 8, dis * 29 - 28, 134, 20, 0xf9c569)
        ChangeUI_Button[dis]:SetTransparent(0)
        ChangeUI_Button[dis]:SetTouchEnabled(0)

        -- 鼠标滑过
        ChangeUI_Button[dis].script[XE_ONHOVER] = function()
            if ChangeUI_ListBK:IsVisible() == true then
                ChangeUI_Button[dis]:SetTransparent(1)
            end
        end

        ChangeUI_Button[dis].script[XE_ONUNHOVER] = function()
            if ChangeUI_ListBK:IsVisible() == true then
                ChangeUI_Button[dis]:SetTransparent(0)
            end
        end

        ChangeUI_Button[dis].script[XE_LBUP] = function()
            XChangeNewUISkin(dis - 1)
            -- ChangeUI_FontShowAll:SetFontText(ChangeUI_FontList[dis],0xfffec479)
            ChangeUI_ButtonList:SetButtonFrame(0)
            ChangeUI_ListBK:SetVisible(0)
            for index, value in pairs(ChangeUI_Button) do
                ChangeUI_Button[index]:SetTransparent(0)
                ChangeUI_Button[index]:SetTouchEnabled(0)
            end
        end
    end

    ChangeUI_ButtonList.script[XE_LBUP] = function()
        XClickPlaySound(UI_click_new)
        if ChangeUI_ListBK:IsVisible() then
            ChangeUI_ListBK:SetVisible(0)
            for index, value in pairs(ChangeUI_Button) do
                ChangeUI_Button[index]:SetTransparent(0)
                ChangeUI_Button[index]:SetTouchEnabled(0)
            end
        else
            ChangeUI_ListBK:SetVisible(1)
            for index, value in pairs(ChangeUI_Button) do
                ChangeUI_Button[index]:SetTransparent(0)
                ChangeUI_Button[index]:SetTouchEnabled(1)
            end
        end
    end

    -- 鼠标
    MouseSkin_ButtonList = wnd:AddTwoButton(path_setup .. "btn1_voice_2.BMP", path_setup .. "btn2_voice_2.BMP",
        path_setup .. "btn1_voice_2.BMP", 796 + posx_move, 337 + posy_move, 177, 21)
    MouseSkin_FontShowAll = MouseSkin_ButtonList:AddFont("默认", 12, 0, 8, 2, 145, 20, 0xf9c569)

    MouseSkin_ListBK = wnd:AddImage(path_setup .. "voice_bg_2.BMP", 806 + posx_move, 357 + posy_move, 152, 202)
    MouseSkin_ListBK:SetVisible(0)

    for dis = 1, #MouseSkin_FontList do
        MouseSkin_Button[dis] = wnd:AddImage(path_setup .. "voice_select_2.BMP", 806 + posx_move,
            329 + posy_move + dis * 29, 150, 20)
        MouseSkin_TextList[dis] = MouseSkin_ListBK:AddFont(MouseSkin_FontList[dis], 12, 0, 8, dis * 29 - 28, 134, 20,
            0xf9c569)
        MouseSkin_Button[dis]:SetTransparent(0)
        MouseSkin_Button[dis]:SetTouchEnabled(0)

        -- 鼠标滑过
        MouseSkin_Button[dis].script[XE_ONHOVER] = function()
            if MouseSkin_ListBK:IsVisible() == true then
                MouseSkin_Button[dis]:SetTransparent(1)
            end
        end

        MouseSkin_Button[dis].script[XE_ONUNHOVER] = function()
            if MouseSkin_ListBK:IsVisible() == true then
                MouseSkin_Button[dis]:SetTransparent(0)
            end
        end

        MouseSkin_Button[dis].script[XE_LBUP] = function()
            XChangeMouseSkin(MouseSkin_SkinID[dis])
            MouseSkin_FontShowAll:SetFontText(MouseSkin_FontList[dis], 0xfec479)
            MouseSkin_ButtonList:SetButtonFrame(0)
            MouseSkin_ListBK:SetVisible(0)
            for index, value in pairs(MouseSkin_Button) do
                MouseSkin_Button[index]:SetTransparent(0)
                MouseSkin_Button[index]:SetTouchEnabled(0)
            end
        end
    end

    MouseSkin_ButtonList.script[XE_LBUP] = function()
        XClickPlaySound(UI_click_new)
        if MouseSkin_ListBK:IsVisible() then
            MouseSkin_ListBK:SetVisible(0)
            for index, value in pairs(MouseSkin_Button) do
                MouseSkin_Button[index]:SetTransparent(0)
                MouseSkin_Button[index]:SetTouchEnabled(0)
            end
        else
            MouseSkin_ListBK:SetVisible(1)
            for index, value in pairs(MouseSkin_Button) do
                MouseSkin_Button[index]:SetTransparent(0)
                MouseSkin_Button[index]:SetTouchEnabled(1)
            end
        end
    end

    -- 语音包
    BTN_LIST = wnd:AddTwoButton(path_setup .. "btn1_voice_2.BMP", path_setup .. "btn2_voice_2.BMP",
        path_setup .. "btn1_voice_2.BMP", 796 + posx_move, 309 + posy_move, 177, 21)
    Font_showAll = BTN_LIST:AddFont("默认", 12, 0, 8, 2, 145, 20, 0xf9c569)

    LIST_BK = wnd:AddImage(path_setup .. "voice_bg_2.BMP", 806 + posx_move, 329 + posy_move, 152, 202)
    LIST_BK:SetImageFrameWidth(10)
    LIST_BK:SetVisible(0)

    for dis = 1, 7 do
        BTN_VoicePack[dis] = wnd:AddImage(path_setup .. "voice_select_2.BMP", 806 + posx_move,
            300 + posy_move + dis * 29, 150, 20)
        Font_VoicePack[dis] = LIST_BK:AddFont("", 12, 0, 8, dis * 29 - 28, 134, 20, 0xf9c569)
        BTN_VoicePack[dis]:SetTransparent(0)
        BTN_VoicePack[dis]:SetTouchEnabled(0)
        -- 鼠标滑过
        BTN_VoicePack[dis].script[XE_ONHOVER] = function()
            if LIST_BK:IsVisible() == true then
                BTN_VoicePack[dis]:SetTransparent(1)
            end
        end
        BTN_VoicePack[dis].script[XE_ONUNHOVER] = function()
            if LIST_BK:IsVisible() == true then
                BTN_VoicePack[dis]:SetTransparent(0)
            end
        end

        BTN_VoicePack[dis].script[XE_LBUP] = function()
			local index = CurVoicePackIndex + dis - 1
            XSelectVoicePack(BTN_VoicePackId[index])
            Font_showAll:SetFontText(BTN_VoicePackFont[index], 0xfec479)
            BTN_LIST:SetButtonFrame(0)
            LIST_BK:SetVisible(0)
            for index, value in pairs(BTN_VoicePack) do
                BTN_VoicePack[index]:SetTransparent(0)
                BTN_VoicePack[index]:SetTouchEnabled(0)
            end
        end
    end

    BTN_LIST.script[XE_LBUP] = function()
        XClickPlaySound(UI_click_new)
        if LIST_BK:IsVisible() then
            LIST_BK:SetVisible(0)
            for index, value in pairs(BTN_VoicePack) do
                BTN_VoicePack[index]:SetTransparent(0)
                BTN_VoicePack[index]:SetTouchEnabled(0)
            end
        else
            LIST_BK:SetVisible(1)
            for index, value in pairs(BTN_VoicePack) do
                BTN_VoicePack[index]:SetTransparent(0)
                BTN_VoicePack[index]:SetTouchEnabled(1)
            end
        end
    end

    -- 右边滚动条
    scroll_bg = LIST_BK:AddImage("", 150, 2, 4, 42)
    local dx_scroll_btn = scroll_bg:AddButton(path_new_login .. "SelectServer/scroll1.BMP",
        path_new_login .. "SelectServer/scroll1.BMP", path_new_login .. "SelectServer/scroll1.BMP", 0, 0, 6, 42)

    XSetWindowFlag(dx_scroll_btn.id, 1, 1, 0, 150)
    dx_scroll_btn:ToggleBehaviour(XE_ONUPDATE, 1)
    dx_scroll_btn:ToggleEvent(XE_ONUPDATE, 1)
    dx_scroll_btn.script[XE_ONUPDATE] = function()
        if dx_scroll_btn._T == nil then
            dx_scroll_btn._T = 0
        end

        CurVoicePackIndex, dx_scroll_btn._T = DragScrollBar(dx_scroll_btn, 1, 7, #BTN_VoicePackFont, 150,
            CurVoicePackIndex)
        RefreshVoicePackList()
    end

    -- 设置界面可以滑动
    wnd:EnableEvent(XE_MOUSEWHEEL)
    wnd.script[XE_MOUSEWHEEL] = function()
        if LIST_BK:IsVisible() then
            dx_scroll_btn._T = TrundleScrollBar(dx_scroll_btn, 1, 7, #BTN_VoicePackFont, 150, CurVoicePackIndex)
        end
    end

end

function InitMainSetup_GameA(wnd)
    local background = wnd:AddImage(path_setup .. "dragBK1_setup_2.BMP", 817 + posx_move, 512 + posy_move, 150, 14)
    CameraZoom = background:AddImage(path_setup .. "dragBK2_setup_2.BMP", 2, -8, 145, 10)
    wnd:AddFont("视距设置", 15, 0, 812 + posx_move, 490 + posy_move, 100, 20, 0xff8580d2)
    wnd:AddFont("16", 15, 0, 796 + posx_move, 508 + posy_move, 100, 20, 0xff8580d2)
    wnd:AddFont("35", 15, 0, 960 + posx_move, 508 + posy_move, 100, 20, 0xff8580d2)

    local temp_wnd = CameraZoom:AddImage(path_dv .. "R.BMP", 0, 0, 150, 20)
    temp_wnd:SetTransparent(0)
    temp_wnd.script[XE_LBUP] = function()
        local X, Y = CameraZoom:GetPosition()
        local L = XGetCursorPosX() - X
        L = math.max(0, L)
        L = math.min(L, 125)
        XUpDateCameraZoomScrollBarPos(math.floor((math.max(0, math.min(125, L)) / 125) * (CameraZoomMax - CameraZoomMin) + 0.5) + CameraZoomMin)
        CameraZoom:SetAddImageRect(CameraZoom.id, 0, 0, L + 10, 10, 2, 2, L + 10, 10)
        CameraZoomBtn._L = L
        CameraZoomBtn:SetPosition(CameraZoomBtn._L, 0)
    end
    BWnd = CreateWindow(CameraZoom.id, -3, -6, 28, 22)
    BWnd:SetTouchEnabled(0)
    CameraZoomBtn = BWnd:AddButton(path_setup .. "dragBtn_setup_2.BMP", path_setup .. "dragBtn_setup_2.BMP",
        path_setup .. "dragBtn_setup_2.BMP", 0, 0, 28, 22)
    XSetWindowFlag(CameraZoomBtn.id, 1, 2, 0, 125)

    CameraZoomBtn:ToggleBehaviour(XE_ONUPDATE, 1)
    CameraZoomBtn:ToggleEvent(XE_ONUPDATE, 1)

    CameraZoomBtn.script[XE_ONUPDATE] = function()
        if CameraZoomBtn._L == nil then
            CameraZoomBtn._L = 0
        end
        local L, T, R, B = XGetWindowClientPosition(CameraZoomBtn.id)

        if CameraZoomBtn._L ~= L then
            XUpDateCameraZoomScrollBarPos(math.floor((math.max(0, math.min(125, L)) / 125) * (CameraZoomMax - CameraZoomMin) + 0.5) + CameraZoomMin)
            CameraZoom:SetAddImageRect(CameraZoom.id, 0, 0, L + 10, 10, 2, 2, L + 10, 10)
            CameraZoomBtn._L = L
        end
    end

    local posx = {328, 328, 328, 328, 490, 490, 490, 490, 655, 620, 620, 605, 812, 812, 313, 475, 620, 812, 900, 812, 328, 460, 620, 800,900}
    local posy = {419, 455, 491, 527, 419, 455, 491, 527, 419, 455, 491, 527, 419, 455, 558, 558, 558, 558, 527, 527, 589, 589, 589, 589,589}
    local font_name = {"技能提示", "色盲模式", "伤害飘字", "详细血量", "战斗记录", "屏幕震动",
                       "击杀动画", "关闭弹幕", "VIP显示", "普通攻击范围", "关闭启动动画",
                       "小地图快速移动", "死亡后装备栏自动铸魂", "抗锯齿", "小地图左置",
                       "至尊卡显示", "显示英雄头像", "头像置顶（宽 >= 1600）", "语音轮盘",
                       "状态全显", "主播模式", "个人信息隐藏", "关闭皮肤动画","实验室功能","内存优化"}

    for i = 1, #posx do
        if i == 9 then
            wnd:AddFont("VIP", 15, 0, posx[i] + posx_move, posy[i] + posy_move, 200, 20, 0xffffff)
            wnd:AddFont("显示", 15, 0, posx[i] + posx_move + 24, posy[i] + posy_move, 200, 20, 0x8580d2)
        else
            wnd:AddFont(font_name[i], 15, 0, posx[i] + posx_move, posy[i] + posy_move, 200, 20, 0x8580d2)
        end
    end

    local check_posx = {364, 364, 364, 364, 395, 395, 395, 395, 557, 557, 557, 557, 719, 719, 719, 719, 970, 395, 557,
                        719, 970, 970, 880, 395, 557, 719, 880, 970}
    local check_posy = {249, 277, 305, 333, 415, 451, 488, 523, 415, 451, 488, 523, 415, 451, 488, 523, 415, 553, 553,
                        553, 553, 523, 523, 587, 587, 587, 587, 587}

    for i = 1, #check_posx do
        check_list[i] = wnd:AddImage(path_hero .. "checkbox_hero_2.BMP", check_posx[i] + posx_move,
            check_posy[i] + posy_move, 28, 28)
        check_list[i]:SetTouchEnabled(1)
        -- check_list[i]:AddFont(i, 15, 8, 0, 0, 28, 28, 0x8580d2)
        check_pattern[i] = check_list[i]:AddImage(path_hero .. "checkboxYes_hero_2.BMP", 1, -1, 28, 28)
        check_pattern[i]:SetTouchEnabled(0)
        check_pattern[i]:SetVisible(1)

        check_list[i].script[XE_LBUP] = function()
            if (check_pattern[i]:IsVisible()) then
                check_pattern[i]:SetVisible(0)
                XClickOtherCheckButton_Set(1, i - 1, 0)
            else
                check_pattern[i]:SetVisible(1)
                XClickOtherCheckButton_Set(1, i - 1, 1)
            end
        end
    end

    -- 抗锯齿
    AntiAlias = wnd:AddTwoButton(path_setup .. "btn1_voice_2.BMP", path_setup .. "btn2_voice_2.BMP",
        path_setup .. "btn1_voice_2.BMP", 868 + posx_move, 457 + posy_move, 105, 20)
    AntiAliasFont = AntiAlias:AddFont(AntiAliasFontItem[1], 12, 8, 5, 0, 105, 20, 0xFFFFFF)

    AntiAliasBK = wnd:AddImage(path_setup .. "voice_bg_2.BMP", 878 + posx_move, 477 + posy_move, 86, 102)
    AntiAliasBK:SetImageFrameWidth(10)
    AntiAliasBK:SetVisible(0)

    for dis = 1, #AntiAliasFontItem do
        AntiAliasListBK[dis] = wnd:AddImage(path_setup .. "voice_select_2.BMP", 878 + posx_move,
            458 + posy_move + dis * 20, 84, 20)
        AntiAliasListFont[dis] = AntiAliasBK:AddFont(AntiAliasFontItem[dis], 12, 0, 22, dis * 20 - 17, 84, 20, 0xFFFFFF)
        AntiAliasListBK[dis]:SetTransparent(0)
        AntiAliasListBK[dis]:SetTouchEnabled(0)

        -- 鼠标滑过
        AntiAliasListBK[dis].script[XE_ONHOVER] = function()
            if AntiAliasBK:IsVisible() == true then
                AntiAliasListBK[dis]:SetTransparent(1)
            end
        end
        AntiAliasListBK[dis].script[XE_ONUNHOVER] = function()
            if AntiAliasBK:IsVisible() == true then
                AntiAliasListBK[dis]:SetTransparent(0)
            end
        end
        AntiAliasListBK[dis].script[XE_LBUP] = function()
            XAAdetailOnComboBoxSelChange(1, dis - 1)
            AntiAliasFont:SetFontText(AntiAliasFontItem[dis], 0xFFFFFF)
            index_AntiAlias = dis

            AntiAlias:SetButtonFrame(0)
            AntiAliasBK:SetVisible(0)
            for index, value in pairs(AntiAliasListBK) do
                AntiAliasListBK[index]:SetTransparent(0)
                AntiAliasListBK[index]:SetTouchEnabled(0)
            end
        end
    end

    AntiAlias.script[XE_LBUP] = function()
        XClickPlaySound(Sound_click)
        if AntiAliasBK:IsVisible() then
            AntiAliasBK:SetVisible(0)
            for index, value in pairs(AntiAliasListBK) do
                AntiAliasListBK[index]:SetTransparent(0)
                AntiAliasListBK[index]:SetTouchEnabled(0)
            end
        else
            AntiAlias:SetButtonFrame(1)
            AntiAliasBK:SetVisible(1)
            for index, value in pairs(AntiAliasListBK) do
                AntiAliasListBK[index]:SetTransparent(0)
                AntiAliasListBK[index]:SetTouchEnabled(1)
            end
        end
    end
end

function InitGameSetUiCheckButton(settings)
    printTable(settings)
    for i = 1, #settings do
        if check_pattern[i] then
            check_pattern[i]:SetVisible(settings[i] and 1 or 0)
        end
    end
end

function ForbidNewSingleSet(b)
    if check_list[22] ~= nil then
        check_pattern[22]:SetEnabled(b)
        check_list[22]:SetEnabled(b)
    end
end

function InitScrollBar(a, b, c, d, e, f, g)
    -- 音效
    if A1 == nil then
        A1._L = 0
    else
        A1._L = a / MAXVALUE * 125
    end
    A1:SetPosition(A1._L, 0)
    XSetAddImageRect(AA.id, 0, 0, A1._L + 10, 10, 392 + posx_move, 258 + posy_move, A1._L + 10, 10)
    AP_FONT = string.format("%d", (A1._L / 125) * MAXVALUE)
    AP:SetFontText(AP_FONT .. "%", 0xffffff)

    -- 音乐
    if B1 == nil then
        B1._L = 0
    else
        B1._L = b / MAXVALUE * 125
    end
    B1:SetPosition(B1._L, 0)
    XSetAddImageRect(BB.id, 0, 0, B1._L + 10, 10, 392 + posx_move, 287 + posy_move, B1._L + 10, 10)
    BP_FONT = string.format("%d", (B1._L / 125) * MAXVALUE)
    BP:SetFontText(BP_FONT .. "%", 0xffffff)

    -- 声音
    if C1 == nil then
        C1._L = 0
    else
        C1._L = c / MAXVALUE * 125
    end
    C1:SetPosition(C1._L, 0)
    XSetAddImageRect(CC.id, 0, 0, C1._L + 10, 10, 392 + posx_move, 314 + posy_move, C1._L + 10, 10)
    CP_FONT = string.format("%d", (C1._L / 125) * MAXVALUE)
    CP:SetFontText(CP_FONT .. "%", 0xffffff)

    -- 语音
    if F1 == nil then
        F1._L = 0
    else
        F1._L = f / MAXVALUE * 125
    end
    F1:SetPosition(F1._L, 0)
    XSetAddImageRect(FF.id, 0, 0, F1._L + 10, 10, 392 + posx_move, 343 + posy_move, F1._L + 10, 10)
    FP_FONT = string.format("%d", (F1._L / 125) * MAXVALUE)
    FP:SetFontText(FP_FONT .. "%", 0xffffff)

    -- 小地图
    if D1 == nil then
        D1._L = 0
    else
        D1._L = d / MAXVALUE * 125
    end
    D1:SetPosition(D1._L, 0)
    XSetAddImageRect(DD.id, 0, 0, D1._L + 10, 10, 820 + posx_move, 258 + posy_move, D1._L + 10, 10)
    DP_FONT = string.format("%d", (D1._L / 125) * MAXVALUE)
    DP:SetFontText(DP_FONT .. "%", 0x83d1e7)

    -- 滚屏速度
    if E1 == nil then
        E1._L = 0
    else
        E1._L = e / 1000 * 125
    end
    E1:SetPosition(E1._L, 0)
    XSetAddImageRect(EE.id, 0, 0, E1._L + 10, 10, 820 + posx_move, 287 + posy_move, E1._L + 10, 10)
    EP_FONT = string.format("%d", (E1._L / 125) * MAXVALUE)
    EP:SetFontText(EP_FONT .. "%", 0x83d1e7)

    if CameraZoom ~= nil then
        local temp_lenght = ((math.max(CameraZoomMin, math.min(CameraZoomMax, g)) - CameraZoomMin) / (CameraZoomMax - CameraZoomMin)) * 125
        if g == CameraZoomMax then
            temp_lenght = 125
        elseif g == CameraZoomMin then
            temp_lenght = 0
        end
        CameraZoomBtn._L = temp_lenght
        CameraZoomBtn:SetPosition(CameraZoomBtn._L, 0)
        CameraZoom:SetAddImageRect(CameraZoom.id, 0, 0, temp_lenght + 10, 10, 2, 2, temp_lenght + 10, 10)
    end
end

function ClearVoicePackList()
    CurVoicePackIndex = 1
    BTN_VoicePackFont = {}
    BTN_VoicePackId = {}
    Font_showAll:SetFontText("", 0xfec479)
    LIST_BK:SetVisible(0)
    BTN_LIST:SetButtonFrame(0)

    for index, value in pairs(BTN_VoicePack) do
        BTN_VoicePack[index]:SetVisible(0)
    end

    for index, value in pairs(Font_VoicePack) do
        Font_VoicePack[index]:SetVisible(0)
    end

    InitVoicePackList("默认", 0)
end

function InitVoicePackList(cTalentName, itemid)
    local index = #BTN_VoicePackFont + 1
    BTN_VoicePackFont[index] = cTalentName
    BTN_VoicePackId[index] = itemid

    if #BTN_VoicePackFont > 7 then
        LIST_BK:SetWH(152, 202)
    else
        LIST_BK:SetWH(152, 29 * #BTN_VoicePackFont + 2)
    end
end

function RefreshVoicePackList()
    if #BTN_VoicePackFont > #BTN_VoicePack then
        scroll_bg:SetVisible(1)
    else
        scroll_bg:SetVisible(0)
    end

    for i = 1, #Font_VoicePack do
        Font_VoicePack[i]:SetVisible(0)
        BTN_VoicePack[i]:SetVisible(0)
    end

    for i = 1, 7 do
        local index = CurVoicePackIndex + i - 1
        if BTN_VoicePackFont[index] ~= nil then
            BTN_VoicePack[i]:SetVisible(1)
            Font_VoicePack[i]:SetFontText(BTN_VoicePackFont[index], 0xfec479)
            Font_VoicePack[i]:SetVisible(1)
        else
            BTN_VoicePack[i]:SetVisible(0)
            Font_VoicePack[i]:SetVisible(0)
        end
    end
end

function SetCurVoicePack(cTalentName)
    Font_showAll:SetFontText(cTalentName, 0xfec479)
end

-- 抗锯齿
function Clear_AntiAlias()
    AntiAliasFontItem = {}
    for i, v in pairs(AntiAliasListFont) do
        AntiAliasListFont[i]:SetVisible(0)
        AntiAliasListBK[i]:SetVisible(0)
    end
end

function SendAntiAliasToLua(Font)
    local size = 0
    if AntiAliasFontItem == {} then
        size = 1
    else
        size = #AntiAliasFontItem + 1
    end
    if Font == 0 then
        Font = "关闭"
    else
        Font = Font .. "倍"
    end
    AntiAliasFontItem[size] = Font

    AntiAliasBK:SetWH(86, 20 * size + 2)
    AntiAliasListFont[size]:SetFontText(Font, 0xFFFFFF)
    AntiAliasListFont[size]:SetVisible(1)
    AntiAliasListBK[size]:SetVisible(1)
end

function InitEffect_SetCheckBoxList(cAAdetailIndex) -- , cMapdetailIndex, cBuilddetailIndex, cPicturedetailIndex, cTerraindetailIndex)
    -- 抗锯齿细节
    AntiAliasFont:SetFontText(AntiAliasFontItem[cAAdetailIndex + 1], 0xFFFFFF)
    index_AntiAlias = cAAdetailIndex + 1

    AntiAlias:SetButtonFrame(0)
    AntiAliasBK:SetVisible(0)
    for index, value in pairs(AntiAliasListBK) do
        AntiAliasListBK[index]:SetTransparent(0)
        AntiAliasListBK[index]:SetTouchEnabled(0)
    end
end

function ClearMouseSkinList()
    MouseSkin_FontList = {}
    MouseSkin_SkinID = {}
    MouseSkin_FontShowAll:SetFontText("", 0xfec479)
    MouseSkin_ListBK:SetVisible(0)
    MouseSkin_ButtonList:SetButtonFrame(0)

    for index, value in pairs(MouseSkin_Button) do
        MouseSkin_Button[index]:SetVisible(0)
    end

    for index, value in pairs(MouseSkin_TextList) do
        MouseSkin_TextList[index]:SetVisible(0)
    end

    InitMouseSkinList("默认", 0)
end

function InitMouseSkinList(cTalentName, itemid)
    local index = #MouseSkin_FontList + 1
    MouseSkin_FontList[index] = cTalentName
    MouseSkin_SkinID[index] = itemid
    MouseSkin_Button[index]:SetVisible(1)
    MouseSkin_TextList[index]:SetFontText(cTalentName, 0xfec479)
    MouseSkin_TextList[index]:SetVisible(1)
    -- XSetAddImageRect(MouseSkin_ListBK.id, 0, 0, 140, index*29, 806+posx_move, 357+posy_move, 140, index*29)
end

function SetCurMouseSkin(cTalentName)
    MouseSkin_FontShowAll:SetFontText(cTalentName, 0xfec479)
end

function IsFocusOn_SetupGame()
    if (g_setup_game_ui:IsVisible() == true) then
        local flagA = LIST_BK:IsVisible() == true and BTN_LIST:IsFocus() == false and BTN_VoicePack[1]:IsFocus() ==
                          false and BTN_VoicePack[2]:IsFocus() == false and BTN_VoicePack[3]:IsFocus() == false and
                          BTN_VoicePack[4]:IsFocus() == false and BTN_VoicePack[5]:IsFocus() == false and
                          BTN_VoicePack[6]:IsFocus() == false and BTN_VoicePack[7]:IsFocus() == false and
                          BTN_VoicePack[8]:IsFocus() == false and BTN_VoicePack[9]:IsFocus() == false and
                          BTN_VoicePack[10]:IsFocus() == false and BTN_VoicePack[11]:IsFocus() == false and
                          BTN_VoicePack[12]:IsFocus() == false

        if (flagA == true) then
            LIST_BK:SetVisible(0)
            BTN_LIST:SetButtonFrame(0)
            for index, value in pairs(BTN_VoicePack) do
                BTN_VoicePack[index]:SetTransparent(0)
                BTN_VoicePack[index]:SetTouchEnabled(0)
            end
        end

        ----抗锯齿细节
        local flagG =
            (AntiAliasBK:IsVisible() == true and AntiAlias:IsFocus() == false and AntiAliasListBK[1]:IsFocus() == false and
                AntiAliasListBK[2]:IsFocus() == false and AntiAliasListBK[3]:IsFocus() == false and
                AntiAliasListBK[4]:IsFocus() == false and AntiAliasListBK[5]:IsFocus() == false)

        if (flagG == true) then
            AntiAlias:SetButtonFrame(0)
            AntiAliasBK:SetVisible(0)
            for index, value in pairs(AntiAliasListBK) do
                AntiAliasListBK[index]:SetTransparent(0)
                AntiAliasListBK[index]:SetTouchEnabled(0)
            end
        end
    end
end

function IsFocusToMouseSkin_SetupGame()
    if g_setup_game_ui:IsVisible() == true then
        local flagA = MouseSkin_ListBK:IsVisible() == true and MouseSkin_ButtonList:IsFocus() == false and
                          MouseSkin_Button[1]:IsFocus() == false and MouseSkin_Button[2]:IsFocus() == false and
                          MouseSkin_Button[3]:IsFocus() == false and MouseSkin_Button[4]:IsFocus() == false and
                          MouseSkin_Button[5]:IsFocus() == false and MouseSkin_Button[6]:IsFocus() == false and
                          MouseSkin_Button[7]:IsFocus() == false and MouseSkin_Button[8]:IsFocus() == false

        if (flagA == true) then
            MouseSkin_ListBK:SetVisible(0)
            MouseSkin_ButtonList:SetButtonFrame(0)
            for index, value in pairs(MouseSkin_Button) do
                MouseSkin_Button[index]:SetTransparent(0)
                MouseSkin_Button[index]:SetTouchEnabled(0)
            end
        end
    end
end

function IsFocusToChangeUI_SetupGame()
    if g_setup_game_ui:IsVisible() == true then
        local flagA = ChangeUI_ListBK:IsVisible() == true and ChangeUI_ButtonList:IsFocus() == false and
                          ChangeUI_Button[1]:IsFocus() == false and ChangeUI_Button[2]:IsFocus() == false

        if (flagA == true) then
            ChangeUI_ListBK:SetVisible(0)
            ChangeUI_ButtonList:SetButtonFrame(0)
            for index, value in pairs(ChangeUI_Button) do
                ChangeUI_Button[index]:SetTransparent(0)
                ChangeUI_Button[index]:SetTouchEnabled(0)
            end
        end
    end
end

function SetChangeUIEditText(index)
    ChangeUI_FontShowAll:SetFontText(ChangeUI_FontList[index], 0xfffec479)
end

-- 取消勾选
function Set_SetupGameTriggerBehaviour(i)
    if check_pattern[i]:IsVisible() == true then
        check_list[i]:TriggerBehaviour(XE_LBUP)
    end
end

-- 设置显示
function Set_SetupGameIsVisible(flag)
    if g_setup_game_ui ~= nil then
        if flag == 1 and g_setup_game_ui:IsVisible() == false then
            -- g_setup_game_ui:CreateResource()
            g_setup_game_ui:SetVisible(1)
            XSetCustomSetVisible_Tab(1, 1)
            XCheckChangeUISkinIndex()

            XInGameLog("act=WINDOW,Function=Set_SetupGameIsVisible,visible=true")
        elseif flag == 0 and g_setup_game_ui:IsVisible() == true then
            -- g_setup_game_ui:DeleteResource()
            g_setup_game_ui:SetVisible(0)
            XSetCustomSetVisible_Tab(1, 0)

            -- XInGameLog("act=WINDOW,Function=Set_SetupGameIsVisible,visible=false")
        end
    end
end

function Get_SetupGameIsVisible()
    if (g_setup_game_ui ~= nil and g_setup_game_ui:IsVisible()) then
        return 1
    else
        return 0
    end
end

function GetSetupCameraZoomValue()
    return CameraZoomMax
end
