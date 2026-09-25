include("../Data/Script/Common/include.lua")

-------设置主界面
local Font_lock = nil
local Font_safe = nil
local font_list = {"（财产未加锁）", "（财产已加锁）"}
local flag_lock = 0

local press_index = 0

local posx_move = -234
local posy_move = -140

local checkA = nil
local checkB = nil
local checkC = nil
local checkD = nil
local checkE = nil

local checkF = nil
local checkF_font = nil
local checkF_Type = 0

local checkH = nil
local checkI = nil
local checkJ = nil
local checkK = nil
local checkL = nil

local checkU = nil

local DownloadButton = nil
-- 异步下载
local BtnAsyncDownload = nil -- 异步文件下载按钮

local ReportBtn = nil -- 举报按钮

local setbuttonlist = {} -- 画面设置的按钮
local funbuttonlist = {} -- 功能设置的按钮
local ImgAsyncDownloadProgressFont = nil
local ImgAsyncDownloadProgressbg = nil
local ImgAsyncDownloadProgress = nil -- 异步下载的进度
local exitbutton = nil
local agreeSurrenderButton = nil

function InitSetup_UI(wnd, bisopen)
    g_setup_ui = CreateWindow(wnd.id, 0, 0, 1920, 1080)
    g_setup_ui:EnableBlackBackgroundTop(1)
    InitMain_Setup(g_setup_ui)
    g_setup_ui:SetVisible(bisopen)
end

function InitMain_Setup(wnd)
    local BK = wnd:AddImage(path_lolshopbuy .. "shopbuybg.BMP", 18, 18, 783, 536)
    BK:SetImageFrameWidth(50)
    BK:AddFont("系统设置", 18, 8, 0, 0, 783, 42, 0xffe684)

    wnd:AddFont("设置", 18, 0, 300 + posx_move, 243 + posy_move, 155, 18, 0xffe684)

    wnd:AddFont("功能", 18, 0, 300 + posx_move, 406 + posy_move, 155, 18, 0xffe684)

    setbuttonlist[1] = wnd:AddButton(path_setup .. "btnBlue1_setup_2.BMP", path_setup .. "btnBlue2_setup_2.BMP",
        path_setup .. "btnBlue3_setup_2.BMP", 307 + posx_move, 282 + posy_move, 184, 49)
    setbuttonlist[1]:AddFont("画面设置", 18, 8, 0, 0, 184, 49, 0xffffff)
    setbuttonlist[1].script[XE_LBUP] = function()
        XClickPlaySound(UI_click_new)

        XSetFaceUiVisible_Tab(1, 1)
    end

    setbuttonlist[2] = wnd:AddButton(path_setup .. "btnBlue1_setup_2.BMP", path_setup .. "btnBlue2_setup_2.BMP",
        path_setup .. "btnBlue3_setup_2.BMP", 557 + posx_move, 282 + posy_move, 184, 49)
    setbuttonlist[2]:AddFont("游戏设置", 18, 8, 0, 0, 184, 49, 0xffffff)
    setbuttonlist[2].script[XE_LBUP] = function()
        XClickPlaySound(UI_click_new)

        Set_SetupGameIsVisible(1)
    end
    setbuttonlist[3] = wnd:AddButton(path_setup .. "btnBlue1_setup_2.BMP", path_setup .. "btnBlue2_setup_2.BMP",
        path_setup .. "btnBlue3_setup_2.BMP", 812 + posx_move, 282 + posy_move, 184, 49)
    setbuttonlist[3]:AddFont("按键设置", 18, 8, 0, 0, 184, 49, 0xffffff)
    setbuttonlist[3].script[XE_LBUP] = function()
        XClickPlaySound(UI_click_new)

        Set_SetupKeypressIsVisible(1)
    end
    funbuttonlist[1] = wnd:AddButton(path_setup .. "btnBlue1_setup_2.BMP", path_setup .. "btnBlue2_setup_2.BMP",
        path_setup .. "btnBlue3_setup_2.BMP", 307 + posx_move, 445 + posy_move, 184, 49)
    funbuttonlist[1]:AddFont("举报/屏蔽", 18, 8, 0, 0, 184, 49, 0xffffff)
    funbuttonlist[1].script[XE_LBUP] = function()
        XClickPlaySound(UI_click_new)

        XShow_SetupAccuse(1)
    end
	funbuttonlist[1]:SetVisible(0)

    -- 举报按钮
    funbuttonlist[2] = wnd:AddButton(path_setup .. "btnBlue1_setup_2.BMP", path_setup .. "btnBlue2_setup_2.BMP",
        path_setup .. "btnBlue3_setup_2.BMP", 307 + posx_move, 445 + posy_move, 184, 49)
    funbuttonlist[2]:AddFont("举报", 18, 8, 0, 0, 184, 49, 0xffffff)
    funbuttonlist[2].script[XE_LBUP] = function()
        XClickPlaySound(UI_click_new)
        XReqReportPlayerInfoList()
        SetReportWndVisible(1)
    end

    -- 资源下载按钮
    funbuttonlist[3] = wnd:AddButton(path_setup .. "btnBlue1_setup_2.BMP", path_setup .. "btnBlue2_setup_2.BMP",
        path_setup .. "btnBlue3_setup_2.BMP", 307 + posx_move, 506 + posy_move, 184, 49)
    funbuttonlist[3]:AddFont("资源下载", 18, 8, 0, 0, 184, 49, 0xffffff)
    funbuttonlist[3].script[XE_LBUP] = function()
        XClickPlaySound(UI_click_new)
        XSetupDownload()
    end

    -- 新的资源下载按钮
    funbuttonlist[4] = wnd:AddButton(path_setup .. "btnBlue1_setup_2.BMP", path_setup .. "btnBlue2_setup_2.BMP",
        path_setup .. "btnBlue3_setup_2.BMP", 557 + posx_move, 343 + posy_move, 184, 49)
    ImgAsyncDownloadProgressFont = funbuttonlist[4]:AddFont("资源下载", 18, 8, 0, 0, 184, 49, 0xffffff)
    funbuttonlist[4]:SetVisible(0)
    funbuttonlist[4].script[XE_LBUP] = function()
        XAsyncConfirmDownload()
    end

    -- 资源下载百分比
    ImgAsyncDownloadProgressbg = funbuttonlist[4]:AddImage(path_async .. "loading_setting_progress_bg.BMP", 26, 30, 128, 5)
    ImgAsyncDownloadProgressbg:SetVisible(0)
    ImgAsyncDownloadProgress = ImgAsyncDownloadProgressbg:AddImage(path_async .. "loading_setting_progress.BMP", 1, 1, 126, 3)


    funbuttonlist[5] = wnd:AddButton(path_setup .. "btnBlue1_setup_2.BMP", path_setup .. "btnBlue2_setup_2.BMP",
        path_setup .. "btnBlue3_setup_2.BMP", 557 + posx_move, 445 + posy_move, 184, 49)
    funbuttonlist[5]:AddFont("账号安全锁", 18, 8, 0, 0, 184, 49, 0xffffff)
    funbuttonlist[5].script[XE_LBUP] = function()
        XClickPlaySound(UI_click_new)
        XLockOnButtonClick_Safe()
    end
    funbuttonlist[6] = wnd:AddButton(path_setup .. "btnBlue1_setup_2.BMP", path_setup .. "btnBlue2_setup_2.BMP",
        path_setup .. "btnBlue3_setup_2.BMP", 812 + posx_move, 445 + posy_move, 184, 49)
    checkF_font = funbuttonlist[6]:AddFont("更换账号", 18, 8, 0, 0, 184, 49, 0xffffff)
    funbuttonlist[6].script[XE_LBUP] = function()
        XClickPlaySound(UI_click_new)
        Set_SetupSafeIsVisible(0)
        if checkF_Type == 0 then
            XGameRelogin(1) -- 更换账号
        elseif checkF_Type == 1 then
            XExitGame() -- 离开恶龙
        elseif checkF_Type == 2 then
            XExitGame() -- 离开战场
        elseif checkF_Type == 3 then
            XExitSurrender(1) -- 投降
        elseif checkF_Type == 4 then
            XExitView() -- 离开观战
            XReqReplayEvent(7,0)
            ReportReplayEvent()
            SetReplayIsVisible(0)
        elseif checkF_Type == 5 then
            XExitGame() -- 离开桑尼号
        end
    end
    exitbutton = wnd:AddButton(path_lolcommon .. "yes1.BMP", path_lolcommon .. "yes2.BMP",
        path_lolcommon .. "yes3.BMP", 568 + posx_move, 635 + posy_move, 166, 55)
    exitbutton:AddFont("退出游戏", 15, 8, 0, 0, 166, 55, 0xffffff)
    exitbutton.script[XE_LBUP] = function()
        XClickPlaySound(UI_click_new)
        XGameCloseWindow(1)
    end

    funbuttonlist[8] = wnd:AddButton(path_setup .. "btnBlue1_setup_2.BMP", path_setup .. "btnBlue2_setup_2.BMP",
        path_setup .. "btnBlue3_setup_2.BMP", 812 + posx_move, 575 + posy_move, 184, 49)
    local checkU_font = funbuttonlist[8]:AddFont("新引擎测试", 18, 8, 0, 0, 184, 49, 0xffffff)
    funbuttonlist[8].script[XE_LBUP] = function()
        XClickPlaySound(UI_click_new)
        SetMatingType(-1)
        XGameStartUnity()
    end

    -------------关闭界面	
    local btn_close = wnd:AddButton(path_lolcommon .. "close1.BMP", path_lolcommon .. "close2.BMP",
        path_lolcommon .. "close3.BMP", 1012 + posx_move, 145 + posy_move, 33, 34)
    btn_close.script[XE_LBUP] = function()
        XClickPlaySound(UI_click_new)
        XClickCloseSetupUi(1)
        Set_SetupIsVisible(0)
    end

    funbuttonlist[9] = wnd:AddButton(path_setup .. "btnBlue1_setup_2.BMP", path_setup .. "btnBlue2_setup_2.BMP",
        path_setup .. "btnBlue3_setup_2.BMP", 812 + posx_move, 343 + posy_move, 184, 49)
    funbuttonlist[9]:AddFont("NVIDIA Highlights", 15, 8, 0, 0, 184, 49, 0xffffff)
    funbuttonlist[9].script[XE_LBUP] = function()
        XClickPlaySound(Sound_click)

        Set_SetupOtherIsVisible(1)
    end

    setbuttonlist[4] = wnd:AddButton(path_setup .. "btnBlue1_setup_2.BMP", path_setup .. "btnBlue2_setup_2.BMP",
        path_setup .. "btnBlue3_setup_2.BMP", 307 + posx_move, 343 + posy_move, 184, 49)
    setbuttonlist[4]:AddFont("蒂塔魔方", 18, 8, 0, 0, 184, 49, 0xffffff)
    setbuttonlist[4].script[XE_LBUP] = function()
        XClickPlaySound(Sound_click)

        Set_SetupBoxIsVisible(1)
    end

    setbuttonlist[5] = wnd:AddButton(path_setup .. "btnBlue1_setup_2.BMP", path_setup .. "btnBlue2_setup_2.BMP",
        path_setup .. "btnBlue3_setup_2.BMP", 557 + posx_move, 343 + posy_move, 184, 49)
    setbuttonlist[5]:AddFont("语音设置", 18, 8, 0, 0, 184, 49, 0xffffff)
    setbuttonlist[5].script[XE_LBUP] = function()
        XClickPlaySound(UI_click_new)

        Set_SetupVoiceIsVisible(1)
    end
    setbuttonlist[5]:SetVisible(0)

    funbuttonlist[7] = wnd:AddButton(path_setup .. "btnBlue1_setup_2.BMP", path_setup .. "btnBlue2_setup_2.BMP",
        path_setup .. "btnBlue3_setup_2.BMP", 557 + posx_move, 343 + posy_move, 184, 49)
    funbuttonlist[7]:AddFont("自动录制", 18, 8, 0, 0, 184, 49, 0xffffff)
    funbuttonlist[7].script[XE_LBUP] = function()
        XClickPlaySound(UI_click_new)

        Set_SetupVideoIsVisible(1)
    end

    setbuttonlist[6] = wnd:AddButton(path_setup .. "btnBlue1_setup_2.BMP", path_setup .. "btnBlue2_setup_2.BMP",
        path_setup .. "btnBlue3_setup_2.BMP", 557 + posx_move, 343 + posy_move, 184, 49)
    setbuttonlist[6]:AddFont("CDK兑换", 18, 8, 0, 0, 184, 49, 0xffffff)
    setbuttonlist[6].script[XE_LBUP] = function()
        XClickPlaySound(UI_click_new)

        XOpenCDKWeb("https://300activity.jumpw.com/embed/main?")
    end
	
	setbuttonlist[7] = wnd:AddButton(path_setup .. "btnBlue1_setup_2.BMP", path_setup .. "btnBlue2_setup_2.BMP",
        path_setup .. "btnBlue3_setup_2.BMP", 812 + posx_move, 343 + posy_move, 184, 49)
    setbuttonlist[7]:AddFont("修仙新手", 18, 8, 0, 0, 184, 49, 0xffffff)
    setbuttonlist[7].script[XE_LBUP] = function()
        XClickPlaySound(UI_click_new)
		Set_SetupXiuXianIsVisible(1)
    end
	setbuttonlist[7]:SetVisible(0)

    -- 复用投票窗口的响应接口；不发起新的投降。
    agreeSurrenderButton = wnd:AddButton(path_setup .. "btnBlue1_setup_2.BMP",
        path_setup .. "btnBlue2_setup_2.BMP", path_setup .. "btnBlue3_setup_2.BMP",
        307 + posx_move, 635 + posy_move, 184, 49)
    agreeSurrenderButton:AddFont("同意投降", 18, 8, 0, 0, 184, 49, 0xffffff)
    agreeSurrenderButton.script[XE_LBUP] = function()
        if type(XClickSurrenderResponse) == "function" then
            XClickPlaySound(UI_click_new)
            XClickSurrenderResponse(1)
        end
        RefreshSetupSurrenderButton()
    end
    RefreshSetupSurrenderButton()

    Font_lock = funbuttonlist[5]:AddImage(path_setup .. "unlock_setup_2.BMP", 4, 0, 44, 47)
    Font_safe = Font_lock:AddFont(font_list[1], 15, 0, 45, -25, 400, 20, 0xff3d5e)
end

function SetFontSafeData(str)
    Font_safe:SetFontText(str, 0xff3d5e)
    SetUpLockChange()
end

function Set_Nvidia_IsVisible(ibool)
    funbuttonlist[9]:SetVisible(ibool)
	
	ResetPosition_FunButton()
end

function Set_300Box_IsVisible(ibool)
    setbuttonlist[4]:SetVisible(ibool)
	
	ResetPosition_SetButton()
end

function Set_AutoVideo_IsVisible(ibool)
    funbuttonlist[7]:SetVisible(ibool)
		
	ResetPosition_FunButton()
end

function ForbidCDKActivityIcon(ibool)
   setbuttonlist[6]:SetVisible(ibool)
   
   ResetPosition_SetButton()
end

function Set_Setupcheck_DEnable(ibool)
    funbuttonlist[1]:SetEnabled(ibool)
    funbuttonlist[3]:SetVisible(0)
	
	ResetPosition_FunButton()
end

function SetReportSettingBtnVisible(b)
    funbuttonlist[2]:SetVisible(b)	
    ForbidReportListPlayerBtn(b)
    EnabledEndDataReportButton(b)
	
	ResetPosition_FunButton()
end

function SetUpLockChange()
    local ibool = XGetifLock()
    if (ibool == 1) then
        Font_lock.changeimage(path_setup .. "lock_setup_2.BMP")
    else
        Font_lock.changeimage(path_setup .. "unlock_setup_2.BMP")
    end
end

function SetGameSetUiIsVisible(cVisible)
    setbuttonlist[1]:SetEnabled(cVisible)
end

function checkSetupIsVisible()
    if (g_setup_ui:IsVisible()) then
        return true
    else
        return false
    end
end

function SetCurButtonType_Setup(cStr, cType)
    checkF_font:SetFontText(cStr, 0xffffff)
    checkF_Type = cType
    if cType == -1 then
        funbuttonlist[6]:SetVisible(0)
    else
        funbuttonlist[6]:SetVisible(1)
    end
end

function SetUnityEnterIsVisible(vt)
    funbuttonlist[8]:SetVisible(vt)
	
	ResetPosition_FunButton()
end

function ResetPosition_SetButton()
	local count = 1
	for i,v in pairs(setbuttonlist) do
		if setbuttonlist[i]:IsVisible() == true then
			local x = 250 * ((count - 1) % 3) + 307 + posx_move
			local y = 60 * math.ceil(count / 3) - 60 + 282 + posy_move
			
			setbuttonlist[i]:SetPosition(x, y)
			count = count + 1
		end
	end
end


function ResetPosition_FunButton()
	local count = 1
	for i,v in pairs(funbuttonlist) do
		if funbuttonlist[i]:IsVisible() == true then
			local x = 250 * ((count - 1) % 3) + 307 + posx_move
			local y = 60 * math.ceil(count / 3) - 60 + 445 + posy_move
					
			funbuttonlist[i]:SetPosition(x, y)
			count = count + 1
		end
	end
end

-- 设置显示
function Set_SetupIsVisible(flag)
    if g_setup_ui ~= nil then
        if flag == 1 and g_setup_ui:IsVisible() == false then
            g_setup_ui:CreateResource()
            g_setup_ui:SetVisible(1)
            RefreshSetupSurrenderButton()
            XSetSetupUiIsVisible(1, 1)
            Set_SetupSafeIsVisible(0)
            Set_SetupGameIsVisible(0)
            Set_SetupKeypressIsVisible(0)
            Set_SetupFaceIsVisible(0)
            Set_SetupVoiceIsVisible(0)
            Set_SetupOtherIsVisible(0)
            Set_SetupBoxIsVisible(0)
            Set_SetupVideoIsVisible(0)
			Set_SetupXiuXianIsVisible(0)
            if (XGetMapMode() ~= 3) then
                SetEquip_InsideIsVisible(0)
                SetShop_InsideIsVisible(0)
                SetAchievement_InsideIsVisible(0)
            end

            if XGetFastLogin() == 1 then
                funbuttonlist[5]:SetEnabled(0)
            else
                funbuttonlist[5]:SetEnabled(1)
            end
            -- XInGameLog("act=WINDOW,Function=Set_SetupIsVisible,visible=true")
        elseif flag == 0 and g_setup_ui:IsVisible() == true then
            g_setup_ui:DeleteResource()
            g_setup_ui:SetVisible(0)
            XSetSetupUiIsVisible(1, 0)

            -- XInGameLog("act=WINDOW,Function=Set_SetupIsVisible,visible=false")
        end
    end
end

function Get_SetupIsVisible()
    if g_setup_ui ~= nil and g_setup_ui:IsVisible() == true then
        return 1
    else
        return 0
    end
end

function ShowVoiceSetting(flag)
    setbuttonlist[5]:SetVisible(flag)
	
	ResetPosition_SetButton()
end

---- Async Donwload

function UpdateGameSetUpAsyncDownloadProgress(percent)
    ImgAsyncDownloadProgress:SetAddImageRect(ImgAsyncDownloadProgress.id, 1, 1, 126 * percent, 3, 1, 1, 126 * percent, 3)
end

-- 根据异步下载状态显示控件
function UpdateSetupAsyncUIByState(state)
    -- 游戏设置中的UI
    if state == EASYNCBACKGROUNDDOWNLOADSTATE_NONE then
        funbuttonlist[4]:SetVisible(0)
    elseif state == EASYNCBACKGROUNDDOWNLOADSTATE_FINISH then
        funbuttonlist[4]:SetVisible(0)
    elseif state == EASYNCBACKGROUNDDOWNLOADSTATE_NOSPACE then
        funbuttonlist[4]:SetVisible(1)
		ImgAsyncDownloadProgressFont:SetFontText("资源下载",0xffffff)
        ImgAsyncDownloadProgressbg:SetVisible(0)
    elseif state == EASYNCBACKGROUNDDOWNLOADSTATE_DOWNLOADING then
        funbuttonlist[4]:SetVisible(1)
        ImgAsyncDownloadProgressbg:SetVisible(1)
		ImgAsyncDownloadProgressFont:SetFontText("资源下载中...",0xffffff)
        ImgAsyncDownloadProgressbg:SetVisible(1)
        UpdateGameSetUpAsyncDownloadProgress(XAsyncGetDownloadedFilePercent())
    elseif state == EASYNCBACKGROUNDDOWNLOADSTATE_DOWNLIST_CHECKED then
        funbuttonlist[4]:SetVisible(1)
		ImgAsyncDownloadProgressFont:SetFontText("资源下载",0xffffff)
        ImgAsyncDownloadProgressbg:SetVisible(0)
    elseif state == EASYNCBACKGROUNDDOWNLOADSTATE_FINISH_WITH_FAILURE then
        funbuttonlist[4]:SetVisible(1)
		ImgAsyncDownloadProgressFont:SetFontText("资源下载",0xffffff)
        ImgAsyncDownloadProgressbg:SetVisible(0)
    end
	
	ResetPosition_FunButton()
end

-- 供原投票窗口同步按钮状态，也用于设置窗口重新打开时刷新。
function RefreshSetupSurrenderButton()
    if agreeSurrenderButton ~= nil then
        agreeSurrenderButton:SetVisible(1)
        agreeSurrenderButton:SetEnabled(1)
    end
end
