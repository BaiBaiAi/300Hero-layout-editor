include("../Data/Script/Common/include.lua")

-- 匹配确认界面 - 对应 FGUI BattleReady_1280_800 布局
path_battleready = "../Data/UI/BattleReady/"

-- 背景控件
local bgfx = nil
local bg = nil

-- 按钮
local btnClose = nil
local btnComfirm = nil
local btnComfirmText = nil

-- 文字
local txtGamemode = nil
local title2 = nil
local txtState = nil

-- 玩家头像 (动态创建)
local g_MaxPlayer = 10
local m_HeadsCreated = false
local PlayerBg = {}
local PlayerWait = {}
local PlayerConfirm = {}
local PlayerHeaderIcon = {}
local PlayerMe = {}
local PlayerState = {}
local m_MatchID = 0
local m_RemainSeconds = 0

-- 当前状态
local bIsReady = false
local lastAcceptedMatchID = nil

local curindex = 0

local iconsize = 42

local function HideAllMatchReadyPlayers()
    for i = 1, #PlayerBg do
        PlayerBg[i]:SetVisible(0)
        PlayerWait[i]:SetVisible(0)
        PlayerConfirm[i]:SetVisible(0)
        PlayerMe[i]:SetVisible(0)
        PlayerHeaderIcon[i]:SetVisible(0)
        PlayerState[i] = 0
    end
end

-- 销毁并重建头像
-- 计算玩家头像位置
local function CalcPlayerPos(index, totalCount, centerx, centery, stepx, stepy)
    local totalInRow, row, col
    if totalCount >= 10 then
        -- 两列布局：上下两行，从中心向左右分散
        totalInRow = math.ceil(totalCount / 2)
        row = math.floor((index - 1) / totalInRow)
        col = (index - 1) % totalInRow
    else
        -- 单列布局：一行，从中心向左右分散
        totalInRow = totalCount
        row = 0
        col = index - 1
        centery = centery + iconsize * 0.5
    end
    local offset = (totalInRow - 1) * stepx / 2
    local hx = centerx - offset + col * stepx
    local hy = centery + (row - 0.5) * stepy
    return hx, hy
end

local function RebuildMatchReadyHeads(wnd, count)
    if count <= 0 then return end

    local centerx = 640 - iconsize / 2
    local centery = 390 - iconsize / 2
    local stepx = 60
    local stepy = 46

    -- 先重置：如果现有数量不够，创建新元素
    if count > #PlayerBg then
        for i = #PlayerBg + 1, count do
            local hx, hy = CalcPlayerPos(i, count, centerx, centery, stepx, stepy)
            PlayerBg[i] = wnd:AddImage(
                path_battleready .. "loading_bg40.png", hx + 8, hy + 8, iconsize - 6, iconsize - 6
            )
            PlayerBg[i]:SetVisible(1)

            PlayerWait[i] = wnd:AddImage(
                path_battleready .. "mj_0003_icon-2.png", hx + 8, hy + 8, iconsize - 6, iconsize - 6
            )
            PlayerWait[i]:SetVisible(1)

            PlayerConfirm[i] = wnd:AddImage(
                path_battleready .. "mj_0004_icon-4.png", hx + 5, hy + 5, iconsize, iconsize
            )
            PlayerConfirm[i]:SetVisible(0)

            PlayerHeaderIcon[i] = wnd:AddImage(
                path_battleready .. "mj_0004_icon-4.png", hx + 9, hy + 9, iconsize, iconsize
            )
            PlayerHeaderIcon[i]:SetVisible(0)
            PlayerHeaderIcon[i]:SetScale(0.8)

            PlayerMe[i] = wnd:AddImage(path_battleready .. "loading_bg41.png", hx + 5, hy + 5, iconsize, iconsize)
            PlayerMe[i]:SetVisible(0)

            PlayerState[i] = 0
        end
    end

    HideAllMatchReadyPlayers()

    -- 重新定位所有头像（支持动态数量变化）
    for i = 1, math.min(count, #PlayerBg) do
        local hx, hy = CalcPlayerPos(i, count, centerx, centery, stepx, stepy)
        PlayerBg[i]:SetPosition(hx + 8, hy + 8)
        PlayerWait[i]:SetPosition(hx + 8, hy + 8)
        PlayerConfirm[i]:SetPosition(hx + 5, hy + 5)
        PlayerHeaderIcon[i]:SetPosition(hx + 9, hy + 9)
        PlayerMe[i]:SetPosition(hx + 5, hy + 5)
    end
end

local function SetMatchReadyState(state)
    if state == 0 then
        btnComfirm:SetVisible(1)
        txtState:SetVisible(0)
        title2:SetFontText("已就绪", 0xd3d4ff)
        btnClose:SetVisible(1)
    else
        btnClose:SetVisible(0)
        btnComfirm:SetVisible(0)
        txtState:SetVisible(1)
        title2:SetFontText("等待玩家中", 0xd3d4ff)
        bIsReady = true

        for i = 1, g_MaxPlayer do
            PlayerBg[i]:SetVisible(1)
            PlayerWait[i]:SetVisible(1)
            PlayerConfirm[i]:SetVisible(0)
            PlayerMe[i]:SetVisible(0)
            PlayerHeaderIcon[i]:SetVisible(0)
            PlayerState[i] = 0
        end
    end
end
-- 自动与手动确认共用原生接受接口；每个匹配编号只提交一次。
local function AcceptCurrentMatchReady()
    if g_matchready_ui == nil or not g_matchready_ui:IsVisible()
        or bIsReady or m_MatchID == nil or m_MatchID == 0
        or m_RemainSeconds <= 0 then
        return false
    end
    if lastAcceptedMatchID == m_MatchID then
        SetMatchReadyState(1)
        return false
    end
    if type(XSendMatchReadyAccept) ~= "function" then
        return false
    end
    lastAcceptedMatchID = m_MatchID
    SetMatchReadyState(1)
    XClickPlaySound(UI_click_new)
    XSendMatchReadyAccept(m_MatchID, 1)
    return true
end

local function ResetMatchReadyUI()
    bIsReady = false
    HideAllMatchReadyPlayers()
    SetMatchReadyState(0)
    txtGamemode:SetFontText("", 0xebebff)
    txtState:SetFontText("", 0xbcbcff)
end

function InitMatchReadyUI(wnd, bisopen)
    g_matchready_ui = CreateWindow(wnd.id, 0, 0, 1280, 800)
    g_matchready_ui:EnableBlackBackgroundTop(1)
    InitMain_MatchReady(g_matchready_ui)
    g_matchready_ui:SetVisible(bisopen)
end

function InitMain_MatchReady(wnd)
    bgfx = wnd:AddImage(path_battleready .. "select_glow54.png", 349, 232, 581, 311)
    bgfx:SetTouchEnabled(0)

    bg = wnd:AddImage(path_battleready .. "popup_frame423.png", 349, 234, 581, 312)
    bg:SetTouchEnabled(0)

    local effect = wnd:AddEffectEX(
        "..\\Data\\Magic\\Common\\UI\\changwai\\pipei\\tx_UI_CW_pipei_03.x", 640, 400, 581, 581, 78
    )
    local txtGamemodeWnd = CreateWindow(wnd.id, 561, 299, 158, 32)
    txtGamemode = txtGamemodeWnd:AddFont("", 16, 8, 0, 0, 158, 32, 0xebebff)

    local title2Wnd = CreateWindow(wnd.id, 561, 320, 158, 26)
    title2 = title2Wnd:AddFont("等待玩家中", 14, 8, 0, 0, 158, 26, 0xd3d4ff)

    btnClose = wnd:AddButton(
        path_battleready .. "x_2.png", path_battleready .. "x_1.png", path_battleready .. "x_1.png", 813, 303, 40, 37
    )
    btnClose.script[XE_LBUP] = function ()
        if bIsReady then return end
        XClickPlaySound(UI_click_new)
        -- 1是接受，2是拒绝
        XSendMatchReadyAccept(m_MatchID, 2)
        -- 关闭界面
        SetMatchReadyIsVisible(0, 0, 0, 0, "")
    end

    btnComfirm = wnd:AddButton(
        path_battleready .. "btn_bg_normal.png", path_battleready .. "btn_bg_normal.png",
        path_battleready .. "btn_bg_normal.png", 546, 380, 188, 39
    )
    btnComfirm.script[XE_LBUP] = function ()
        AcceptCurrentMatchReady()
    end

    btnComfirmText = btnComfirm:AddFont("接 受", 16, 8, 0, 0, 188, 39, 0xe9e8fd)

    local contentWnd = CreateWindow(wnd.id, 561, 445, 158, 26)
    txtState = contentWnd:AddFont("", 14, 8, 0, 0, 158, 26, 0xbcbcff)

    SetMatchReadyState(0)

    --[[
    --测试按钮
    local btnComfirm2 = wnd:AddButton(
        path_battleready .. "btn_bg_normal.png", path_battleready .. "btn_bg_normal.png",
        path_battleready .. "btn_bg_normal.png", 200, 200, 100, 30
    )
    btnComfirm2.script[XE_LBUP] = function ()
        XClickPlaySound(UI_click_new)
        curindex = curindex + 1
        local avatar = curindex == 1 and "..\\Data\\UI\\Head\\role\\63071.dds" or ""
        if curindex <= g_MaxPlayer then
            SetMatchReadyPlayer(curindex, 1, curindex == 1 and 1 or 0, avatar)
        else
            SetMatchReadyIsVisible(0, 10, 0, 0, "勇者斗恶龙")
            curindex = 0
        end
    end
    btnComfirm2:AddFont("测试按钮", 30, 8, 0, 0, 100, 30, 0xe9e8fd)
    ]]
end

local function SetMatchReadyGamemode(text)
    text = text or ""
    txtGamemode:SetFontText(text, 0xebebff)
end

local function UpdateMatchReadyPlayerCount()
    local confirmed = 0
    for i = 1, g_MaxPlayer do
        if PlayerState[i] == 1 then
            confirmed = confirmed + 1
        end
    end
    txtState:SetFontText(confirmed .. "/" .. g_MaxPlayer .. "已就绪", 0xbcbcff)
end

function SetMatchReadyPlayer(idx, isConfirmed, isMeIndex, avatar)
    if idx < 1 or idx > g_MaxPlayer then return end

    if not bIsReady then return end

    PlayerBg[idx]:SetVisible(1)
    if isConfirmed == 1 then
        PlayerConfirm[idx]:SetVisible(1)
        PlayerState[idx] = 1
        if avatar ~= nil and avatar ~= "" then
            PlayerHeaderIcon[idx]:SetVisible(1)
            PlayerHeaderIcon[idx].changeimage(avatar)
            log("SetMatchReadyPlayer avatar: " .. avatar)
        end
    else
        PlayerMe[idx]:SetVisible(0)
        PlayerWait[idx]:SetVisible(1)
        PlayerConfirm[idx]:SetVisible(0)
        PlayerHeaderIcon[idx]:SetVisible(0)
    end

     if isMeIndex == idx then
        PlayerMe[idx]:SetVisible(1)
        PlayerState[idx] = 1
        PlayerConfirm[idx]:SetVisible(0)
    end

    UpdateMatchReadyPlayerCount()
end

function SetMatchReadyIsVisible(flag, maxPlayer, uRemainSeconds, uMatchID, mapName)
    if g_matchready_ui ~= nil then
        if flag == 1 and g_matchready_ui:IsVisible() == false then
            -- 每次显示时重新创建头像 (支持动态数量)
            g_MaxPlayer = maxPlayer or 10
            RebuildMatchReadyHeads(g_matchready_ui, g_MaxPlayer)

            g_matchready_ui:CreateResource()
            g_matchready_ui:SetVisible(1)
            bIsReady = false
            SetMatchReadyState(0)
            HideAllMatchReadyPlayers()
            SetMatchReadyGamemode(mapName)
            m_MatchID = uMatchID or 0
            m_RemainSeconds = uRemainSeconds or 0
            -- 必须在匹配编号、剩余时间及界面初始化完成后确认。
            AcceptCurrentMatchReady()
        elseif flag == 0 and g_matchready_ui:IsVisible() == true then
            g_matchready_ui:DeleteResource()
            g_matchready_ui:SetVisible(0)
            ResetMatchReadyUI()
        end
    end
end

function GetMatchReadyIsVisible()
    if g_matchready_ui ~= nil then
        return g_matchready_ui:IsVisible() and 1 or 0
    else
        return 0
    end
end
