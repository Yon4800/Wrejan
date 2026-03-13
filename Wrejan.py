#!/usr/bin/env python3
"""WREJAN v6.66 - 完全無害なギャグウイルス（本物ではない）完全レスポンシブ版"""

import pygame, sys, random, math, time, threading, os, array
try:
    import numpy as np
    NUMPY_OK = True
except ImportError:
    NUMPY_OK = False
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)

BASE_W, BASE_H = 1000, 760
screen = pygame.display.set_mode((BASE_W, BASE_H), pygame.RESIZABLE)
pygame.display.set_caption("WREJAN v6.66  あなたのPCは終わりです")

BLACK=(0,0,0);GREEN=(0,255,70);RED=(255,30,30);YELLOW=(255,230,0)
CYAN=(0,230,255);MAGENTA=(255,0,180);WHITE=(255,255,255)
DARK=(10,10,10);ORANGE=(255,140,0);LIME=(180,255,0)

_font_cache = {}

def _find_jp_font():
    for name in ["msgothic","yugothic","yugothicui","meiryoui","meiryo",
                 "hiraginosansgb","hiraginokakugothicpron",
                 "notosanscjkjp","notosansmonocjkjp","ipagothic","ipapgothic","unifontjp"]:
        try:
            f = pygame.font.SysFont(name, 16)
            s = f.render("あ", True, (255,255,255))
            if s.get_width() > 4:
                return ("sys", name)
        except: pass
    for d in [r"C:\Windows\Fonts","/usr/share/fonts",os.path.expanduser("~/Library/Fonts"),"/System/Library/Fonts"]:
        for fn in ["msgothic.ttc","YuGothR.ttc","meiryo.ttc","NotoSansCJKjp-Regular.otf","IPAGothic.ttf","ipagothic.ttf"]:
            p = os.path.join(d, fn)
            if os.path.exists(p): return ("file", p)
    return None

_JP = _find_jp_font()

def get_font(size, bold=False):
    key = (size, bold)
    if key in _font_cache: return _font_cache[key]
    f = None
    if _JP:
        try:
            f = pygame.font.SysFont(_JP[1],size,bold=bold) if _JP[0]=="sys" else pygame.font.Font(_JP[1],size)
        except: f = None
    if f is None: f = pygame.font.Font(None, size)
    _font_cache[key] = f
    return f

def W(): return screen.get_width()
def H(): return screen.get_height()
def sc(v):  return max(1, int(v * W() / BASE_W))
def scH(v): return max(1, int(v * H() / BASE_H))
def fs(b):  return max(8, sc(b))

def make_beep(freq=440,dur=0.15,vol=0.4,wave="square"):
    sr=44100; n=int(sr*dur); buf=[]
    for i in range(n):
        t=i/sr
        if wave=="square": v=1.0 if math.sin(2*math.pi*freq*t)>0 else -1.0
        elif wave=="sine":  v=math.sin(2*math.pi*freq*t)
        elif wave=="noise": v=random.uniform(-1,1)
        else: v=math.sin(2*math.pi*freq*t)
        fade=1.0
        if i<sr*0.01: fade=i/(sr*0.01)
        elif i>n-sr*0.01: fade=(n-i)/(sr*0.01)
        buf.append(int(v*vol*fade*32767))
    # get_init() で実際のチャンネル数を取得してステレオ対応
    try:
        _, _, actual_ch = pygame.mixer.get_init()
    except Exception:
        actual_ch = 1
    if NUMPY_OK:
        import numpy as np
        arr = np.array(buf, dtype=np.int16)
        if actual_ch == 2:
            arr = np.column_stack([arr, arr])  # モノラル→ステレオ
        return pygame.sndarray.make_sound(arr)
    else:
        # numpy なし: ステレオなら手動インターリーブ
        if actual_ch == 2:
            stereo = []
            for s in buf:
                stereo.append(s); stereo.append(s)
            return pygame.sndarray.make_sound(array.array('h', stereo))
        return pygame.sndarray.make_sound(array.array('h', buf))

def play_evil_laugh():
    def _p():
        for f in [200,250,180,300,150,400,100]: make_beep(f,.08,.5,"square").play();time.sleep(.09)
    threading.Thread(target=_p,daemon=True).start()

def play_alert():
    def _p():
        for f in [880,440,880,440,1760]: make_beep(f,.07,.6,"square").play();time.sleep(.08)
    threading.Thread(target=_p,daemon=True).start()

def play_victory():
    def _p():
        for f in [523,659,784,1047,784,1047,1319]: make_beep(f,.12,.5,"square").play();time.sleep(.13)
    threading.Thread(target=_p,daemon=True).start()

def play_nuclear():
    def _p():
        for i in range(30): make_beep(100+i*40,.05,.7,"square").play();time.sleep(.04)
    threading.Thread(target=_p,daemon=True).start()

class WrejanState:
    def __init__(self):
        self.log_lines=[];self.progress=0.0;self.progress_label=""
        self.glitch_mode=False;self.rainbow_mode=False;self.shake_frames=0
        self.popup_msg="";self.popup_timer=0
        self.cpu_val=0;self.ram_val=0;self.tick=0
        self.active_feat=None;self.completed=set();self.total_damage=0
        self.face_mode="normal";self.scan_angle=0
        self.matrix_chars=[{'xr':random.random(),'y_abs':random.uniform(-1,0),
            'speed':random.uniform(.003,.014),'char':'a'} for _ in range(55)]
    def add_log(self,msg,color=GREEN):
        self.log_lines.append((f"[{time.strftime('%H:%M:%S')}] {msg}",color))
        if len(self.log_lines)>12: self.log_lines.pop(0)
    def popup(self,msg):
        self.popup_msg=msg;self.popup_timer=130

S=WrejanState()

FEATURES=[
    ("[SENTO] 銭湯で...戦闘...w","銭湯に侵入し戦闘開始...「ここは銭湯だ！」「でも...せんとう...w」湯船に沈む"),
    ("[GAME]  ゴェムセンター侵略","ゲームセンターをハック...なぜか「ゴェムセンター」と誤字のまま登録。修正する気ゼロ"),
    ("[FNNN]  ふぬぬぬぬぬ送信","標的に「ふぬぬぬぬぬ」を5億回送信中...受信側も「ふぬぬぬぬぬ」となる。感染成功"),
    ("[NGX]   ﾝｷﾞﾝｸｽ起動","ん...ん...ん......ﾝｷﾞﾝｸｽ！ 謎のエネルギーを解放...何も起きないが本人は満足"),
    ("[HONI]  ほに散布","「ほに」を大気中に散布...半径100kmが「ほに」になった。何が起きたか誰もわからない"),
    ("[NGGG]  んぐぐプロトコル","んぐぐ...んぐぐぐぐ...システムが「んぐぐ」状態に突入。再起動しても「んぐぐ」"),
    ("[GAS]   有鉛スタンダートGS汚染","有鉛スタンダートガソリンをDBに注入中...なぜかエンジンが昭和の音になった"),
    ("[SHW]   シャワー破壊完了","対象のシャワーを遠隔破壊...シャワー破壊完了。なぜかお湯だけ出続けている"),
    ("[SEAL]  あざらし吸引","あざらしを吸う攻撃を実行中...ふわふわ...においがいい...攻撃を忘れた"),
    ("[ZUOL]  ズォールヒ起動","ズォールヒ～～wwww システムがズォールヒ状態に！wwww 意味不明だが超強い"),
    ("[MAYO]  マヨコーン真横展開","マヨコーンを真横に配置中...なぜ真横...斜めでもなく縦でもなく真横...完了"),
    ("[NULL]  ぬるぽ例外発生","NullPointerException: ぬるぽ... ガッ！システムが「ぬるぽ」で落ちた。古の呪い"),
    ("[GUE]   ぐえ送信","全ネットワークに「ぐえ」を送信...ぐえ...ぐえ...サーバーが「ぐえ」で応答"),
    ("[HEX]   六角レンチ抱き枕装備","六角レンチ抱き枕(ステンレス製)を武装...硬い。冷たい。でも離さない。最強の武器"),
    ("[PASS]  パスワード解読","password123...解読完了！天才すぎる(嘘)"),
    ("[BANK]  口座ハッキング","銀行口座を調査中...残高: 0円。あ、もともと空でした(嘘)"),
    ("[NUKE]  核ミサイル起動","核ミサイル発射コード入力中...1234...5678...ぬるぽで落ちた"),
    ("[AI]    AI乗っ取り","ChatGPTハック中...「ふぬぬぬぬぬ」「...は？」「ﾝｷﾞﾝｸｽ！」「帰れ」"),
    ("[ZZZ]   スリープ攻撃","あなたに眠気を送信中...あざらしを吸いながら...zzz...ほに..."),
    ("[END]   全機能解除","Wrejanの機能を全て無効化...完了！ぐえ。最初から無害でした。ズォールヒ～wwww"),
]

FACE_NORMAL=["  +------+  ","  | o  o |  ","  |  v   |  ","  | L__J |  ","  +------+  "]
FACE_EVIL  =["  +------+  ","  | @  @ |  ","  |  w   |  ","  | >--< |  ","  +------+  "]
FACE_DEAD  =["  +------+  ","  | x  x |  ","  |  ^   |  ","  | /--/ |  ","  +------+  "]
FACE_SCARED=["  +------+  ","  | O  O |  ","  |  A   |  ","  | ~~~~ |  ","  +------+  "]
def get_face(): return {"evil":FACE_EVIL,"dead":FACE_DEAD,"scared":FACE_SCARED}.get(S.face_mode,FACE_NORMAL)

def draw_button(surf, bx, by, bw, bh, label, color, hover=False):
    bx,by,bw,bh=int(bx),int(by),int(bw),int(bh)
    alpha=190 if hover else 130
    s=pygame.Surface((bw,bh),pygame.SRCALPHA)
    s.fill((*color[:3],alpha))
    surf.blit(s,(bx,by))
    pygame.draw.rect(surf,color,(bx,by,bw,bh),max(1,sc(2)))
    f=get_font(fs(12))
    r=f.render(label,True,WHITE)
    tx=bx+max(sc(3),(bw-r.get_width())//2)
    ty=by+max(0,(bh-r.get_height())//2)
    prev=surf.get_clip()
    surf.set_clip(pygame.Rect(bx+2,by+2,bw-4,bh-4))
    surf.blit(r,(tx,ty))
    surf.set_clip(prev)

def execute_feature(idx):
    if S.active_feat is not None: return
    name,desc=FEATURES[idx]
    S.active_feat=idx;S.completed.add(idx)
    S.total_damage+=random.randint(1337,9999)
    S.face_mode=random.choice(["evil","evil","scared","dead"])
    S.glitch_mode=True;S.shake_frames=18
    S.add_log(f"EXEC: {name}",YELLOW)
    S.add_log(f"  -> {desc}",CYAN)
    S.progress_label=f"実行中: {name}";S.progress=0.0
    S.popup(f">>> {name} 完了！")
    play_alert()
    def _run():
        for i in range(101): S.progress=i/100.0;time.sleep(.02)
        S.glitch_mode=False
        S.face_mode="evil" if random.random()>.3 else "normal"
        S.add_log(random.choice([
            "-> 完了（何もしてない）ぐえ","-> ほに。以上。","-> んぐぐ...完了",
            "-> ズォールヒ～wwww 終わり","-> ふぬぬぬぬぬ（達成感）",
            "-> 六角レンチを抱きしめながら完了","-> あざらしを吸って落ち着いた",
            "-> ぬるぽ処理完了 ガッ"]),LIME)
        play_evil_laugh();S.active_feat=None
    threading.Thread(target=_run,daemon=True).start()

def calc_btn_grid():
    cw,ch=W(),H()
    pad=sc(10)
    px=sc(16); pw=cw-sc(32)
    COLS=4; ROWS=(len(FEATURES)+COLS-1)//COLS
    # タイトル高さを動的に計算
    tf_h  = get_font(fs(44),bold=True).get_linesize()
    sf_h  = get_font(fs(14),bold=True).get_linesize()
    top_y = scH(8)+tf_h+sf_h+scH(8)
    top_panel_h = int(ch*0.18)
    pb_lbl_y = top_y+top_panel_h+scH(4)
    pb_lbl_h = get_font(fs(12)).get_linesize()
    pb_bar_y = pb_lbl_y+pb_lbl_h+scH(2)
    pb_bar_h = scH(16)
    log_y    = pb_bar_y+pb_bar_h+scH(4)
    log_h    = scH(42)
    hdr_y    = log_y+log_h+scH(6)
    hdr_h    = get_font(fs(13),bold=True).get_linesize()+scH(4)
    area_y   = hdr_y+hdr_h
    area_bot = ch-scH(20)
    area_h   = area_bot-area_y
    cell_w   = (pw-pad*(COLS-1))//COLS
    cell_h   = max(scH(24),(area_h-pad*(ROWS-1))//ROWS)
    return dict(cw=cw,ch=ch,pad=pad,px=px,pw=pw,COLS=COLS,ROWS=ROWS,
                top_y=top_y,top_panel_h=top_panel_h,
                pb_lbl_y=pb_lbl_y,pb_bar_y=pb_bar_y,pb_bar_h=pb_bar_h,
                log_y=log_y,log_h=log_h,hdr_y=hdr_y,area_y=area_y,
                cell_w=cell_w,cell_h=cell_h)

IDLE_MSGS=["待機中... ほに","待機中... あざらしを吸っています","待機中... ﾝｷﾞﾝｸｽの充電中",
           "待機中... 銭湯で戦闘スタンバイ（せんとう...w）","待機中... 六角レンチ抱き枕をぎゅっとしている",
           "待機中... んぐぐ......","待機中... ゴェムセンターを探しています","待機中... マヨコーンを真横に配置中"]
COL_CYCLE=[RED,YELLOW,MAGENTA,CYAN,GREEN,ORANGE]
MATRIX_POOL="ｦｧｨｩｪｫｬｭｮｯｰｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ01ほにぐえ"

def run():
    global screen
    clock=pygame.time.Clock()
    def _uv():
        while True: S.cpu_val=random.randint(97,100);S.ram_val=random.randint(95,100);time.sleep(.5)
    threading.Thread(target=_uv,daemon=True).start()
    S.add_log("WREJAN v6.66 起動...ふぬぬぬぬぬ",RED)
    S.add_log("ターゲットPCに侵入中...ﾝｷﾞﾝｸｽ！",YELLOW)
    S.add_log("銭湯で戦闘準備完了（せんとう...w）",GREEN)
    S.add_log("ゴェムセンター接続OK  ぐえ",CYAN)
    S.add_log("六角レンチ抱き枕(SUS製)装備完了",MAGENTA)
    play_nuclear()

    while True:
        clock.tick(60)
        S.tick+=1; S.scan_angle+=2
        if S.popup_timer>0:  S.popup_timer-=1
        if S.shake_frames>0: S.shake_frames-=1
        cw,ch=W(),H()
        mx,my=pygame.mouse.get_pos()
        ox=random.randint(-sc(4),sc(4)) if S.shake_frames>0 else 0
        oy=random.randint(-sc(3),sc(3)) if S.shake_frames>0 else 0

        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: pygame.quit();sys.exit()
            if ev.type==pygame.VIDEORESIZE:
                screen=pygame.display.set_mode((ev.w,ev.h),pygame.RESIZABLE)
                _font_cache.clear()
            if ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
                L=calc_btn_grid()
                for i in range(len(FEATURES)):
                    ci=i%L['COLS']; ri=i//L['COLS']
                    bx=L['px']+ci*(L['cell_w']+L['pad'])
                    by=L['area_y']+ri*(L['cell_h']+L['pad'])
                    if pygame.Rect(bx,by,L['cell_w'],L['cell_h']).collidepoint(mx-ox,my-oy):
                        execute_feature(i); break

        screen.fill(DARK)
        L=calc_btn_grid()

        # マトリックス雨
        mf=get_font(fs(13))
        for mc in S.matrix_chars:
            mc['y_abs']+=mc['speed']
            if mc['y_abs']>1.0: mc['y_abs']=random.uniform(-.3,0);mc['xr']=random.random()
            mc['char']=random.choice(MATRIX_POOL)
            a=max(0,min(255,int(55+25*math.sin(S.tick*.05))))
            col=(0,a*2//3,0) if not S.glitch_mode else (a,0,0)
            screen.blit(mf.render(mc['char'],True,col),(int(mc['xr']*cw)+ox,int(mc['y_abs']*ch)+oy))

        # タイトル
        tc=COL_CYCLE[(S.tick//8)%len(COL_CYCLE)]
        tf=get_font(fs(44),bold=True)
        t=tf.render("!! W R E J A N !!",True,tc)
        screen.blit(t,(cw//2-t.get_width()//2+ox,scH(8)+oy))
        sf=get_font(fs(14),bold=True)
        s=sf.render("v6.66  ぐえ級ウイルス  ほに  ズォールヒ～～wwww  (完全フィクション)",True,YELLOW)
        screen.blit(s,(cw//2-s.get_width()//2+ox,scH(8)+tf.get_linesize()+scH(3)+oy))

        # 顔
        ff=get_font(fs(14),bold=True); flh=ff.get_linesize()
        face_col=RED if S.glitch_mode else GREEN
        for i,line in enumerate(get_face()):
            screen.blit(ff.render(line,True,face_col),(sc(20)+ox,L['top_y']+i*flh+oy))

        # ステータス
        stf=get_font(fs(13),bold=True); slh=stf.get_linesize()+scH(3)
        sx=sc(195)+ox; sy=L['top_y']+oy
        for i,(st,sc_col) in enumerate([
            (f"CPU: {S.cpu_val}%",RED),(f"RAM: {S.ram_val}%",RED),
            (f"被害: {S.total_damage:,}円",YELLOW),
            (f"実行: {len(S.completed)}/20",CYAN),(f"MODE: {S.face_mode.upper()}",MAGENTA)]):
            screen.blit(stf.render(st,True,sc_col),(sx,sy+i*slh))

        # レーダー
        rr=sc(46); rx=cw-rr-sc(14)+ox; ry=L['top_y']+rr+scH(2)+oy
        pygame.draw.circle(screen,(0,40,0),(rx,ry),rr,1)
        pygame.draw.circle(screen,(0,60,0),(rx,ry),rr*2//3,1)
        ar=math.radians(S.scan_angle)
        pygame.draw.line(screen,GREEN,(rx,ry),(rx+int(rr*math.cos(ar)),ry+int(rr*math.sin(ar))),max(1,sc(2)))
        for _ in range(3):
            pygame.draw.circle(screen,RED,(rx+random.randint(-rr+4,rr-4),ry+random.randint(-rr+4,rr-4)),max(1,sc(2)))

        # プログレスバー
        pf=get_font(fs(12))
        plbl=S.progress_label if S.progress_label else IDLE_MSGS[(S.tick//120)%len(IDLE_MSGS)]
        screen.blit(pf.render(plbl,True,CYAN),(L['px']+ox,L['pb_lbl_y']+oy))
        bby=L['pb_bar_y']; bbh=L['pb_bar_h']; bbw=L['pw']
        pygame.draw.rect(screen,(40,40,40),(L['px']+ox,bby+oy,bbw,bbh))
        filled=int((bbw-4)*S.progress)
        bc=LIME if S.progress<.5 else (YELLOW if S.progress<.9 else RED)
        if filled>0: pygame.draw.rect(screen,bc,(L['px']+2+ox,bby+2+oy,filled,bbh-4))
        pygame.draw.rect(screen,GREEN,(L['px']+ox,bby+oy,bbw,bbh),1)
        pct=get_font(fs(11)).render(f"{int(S.progress*100)}%",True,WHITE)
        screen.blit(pct,(L['px']+bbw//2-pct.get_width()//2+ox,bby+2+oy))

        # ログ
        lf=get_font(fs(11)); llh=scH(19)
        pygame.draw.rect(screen,(5,20,5),(L['px']+ox,L['log_y']+oy,L['pw'],L['log_h']))
        pygame.draw.rect(screen,(0,80,0),(L['px']+ox,L['log_y']+oy,L['pw'],L['log_h']),1)
        for j,(ln,lc) in enumerate(S.log_lines[-2:]):
            screen.blit(lf.render(ln,True,lc),(L['px']+sc(4)+ox,L['log_y']+scH(3)+j*llh+oy))

        # ボタンヘッダ
        hf=get_font(fs(13),bold=True)
        ht=hf.render("[ WREJAN 攻撃メニュー ]  <-ぜんぶ無害",True,YELLOW)
        screen.blit(ht,(L['px']+ox,L['hdr_y']+oy))

        # ボタン
        for i,(bname,_) in enumerate(FEATURES):
            ci=i%L['COLS']; ri=i//L['COLS']
            bx=L['px']+ci*(L['cell_w']+L['pad'])+ox
            by=L['area_y']+ri*(L['cell_h']+L['pad'])+oy
            done=i in S.completed; active=S.active_feat==i
            hover=pygame.Rect(bx-ox,by-oy,L['cell_w'],L['cell_h']).collidepoint(mx,my)
            if active: bc=MAGENTA
            elif done: bc=(0,150,0)
            else:      bc=RED if hover else (80,0,0)
            draw_button(screen,bx,by,L['cell_w'],L['cell_h'],("[OK] " if done else "")+bname,bc,hover)

        # グリッチ
        if S.glitch_mode and random.random()<.4:
            gw=random.randint(sc(50),cw//2)
            gs=pygame.Surface((gw,random.randint(sc(2),sc(8))),pygame.SRCALPHA)
            gs.fill((*random.choice([RED,CYAN,MAGENTA,YELLOW]),80))
            screen.blit(gs,(random.randint(0,cw-gw),random.randint(0,ch)))

        # ポップアップ
        if S.popup_timer>0:
            alpha=min(255,S.popup_timer*4)
            pw=int(cw*.58); ph=scH(56)
            px=cw//2-pw//2+ox; py=ch//2-ph//2+oy
            ps=pygame.Surface((pw,ph),pygame.SRCALPHA); ps.fill((180,0,0,alpha))
            screen.blit(ps,(px,py))
            pygame.draw.rect(screen,YELLOW,(px,py,pw,ph),sc(2))
            popf=get_font(fs(15),bold=True); pt=popf.render(S.popup_msg,True,WHITE)
            screen.blit(pt,(px+pw//2-pt.get_width()//2,py+ph//2-pt.get_height()//2))

        # フッター
        crf=get_font(fs(10))
        cr=crf.render("WREJAN v6.66 (c) ゴェムセンター Evil Corp -- ぐえ -- ほに -- ふぬぬぬぬぬ -- 六角レンチ抱き枕(SUS製) -- 実害ゼロ保証",True,(70,70,70))
        screen.blit(cr,(cw//2-cr.get_width()//2,ch-crf.get_linesize()-scH(3)))

        # レインボー
        if S.rainbow_mode:
            rc=pygame.Surface((cw,ch),pygame.SRCALPHA)
            rc.fill((int(127*(1+math.sin(S.tick*.05))),int(127*(1+math.sin(S.tick*.05+2))),int(127*(1+math.sin(S.tick*.05+4))),28))
            screen.blit(rc,(0,0))

        if len(S.completed)==20 and S.tick%180==0:
            S.add_log("*** 全機能実行！ふぬぬぬぬぬ！ズォールヒ～～wwww！ほに！***",YELLOW)
            S.rainbow_mode=True; play_victory()

        pygame.display.flip()

if __name__=="__main__":
    run()
