import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from backend import FinansalRiskServisi, RiskSeviyesi

# ─── Renk Paleti ─────────────────────────────────────────────────────────────
BG_DARK      = "#0A0E1A"
BG_CARD      = "#111827"
BG_CARD2     = "#1A2235"
ACCENT_BLUE  = "#3B82F6"
ACCENT_CYAN  = "#06B6D4"
ACCENT_GREEN = "#10B981"
ACCENT_RED   = "#EF4444"
ACCENT_AMBER = "#F59E0B"
TEXT_PRIMARY = "#F1F5F9"
TEXT_MUTED   = "#64748B"
TEXT_DIM     = "#94A3B8"
BORDER       = "#1E2D45"
NEON_BLUE    = "#60A5FA"
NEON_CYAN    = "#22D3EE"

# Seviye → renk haritası (backend sabitlerinden türetilir)
SEVİYE_RENK = {
    RiskSeviyesi.YÜKSEK: ACCENT_RED,
    RiskSeviyesi.ORTA:   ACCENT_AMBER,
    RiskSeviyesi.NORMAL: ACCENT_GREEN,
}

# ─── Font Sabitleri ───────────────────────────────────────────────────────────
FONT_TITLE   = ("Courier New", 22, "bold")
FONT_HEADING = ("Courier New", 13, "bold")
FONT_SUBHEAD = ("Courier New", 10, "bold")
FONT_BODY    = ("Courier New", 10)
FONT_MONO    = ("Courier New", 9)
FONT_BIG     = ("Courier New", 28, "bold")
FONT_MED     = ("Courier New", 18, "bold")


# ═════════════════════════════════════════════════════════════════════════════
#  Ana Uygulama Penceresi
# ═════════════════════════════════════════════════════════════════════════════
class FinansalRiskApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Finansal Risk Analiz Sistemi  |  v2.1")
        self.geometry("1280x800")
        self.minsize(1100, 720)
        self.configure(bg=BG_DARK)
        self.resizable(True, True)

        # ── Backend bağlantısı (tek giriş noktası) ───────────────────────────
        self.servis = FinansalRiskServisi()

        # UI state
        self._secili_musteri_id: str | None = None

        self._build_ui()
        self._goster_dashboard()
        self._baslat_canli_saat()

    # ─────────────────────────────────────────────────────────────────────────
    #  UI İskeleti
    # ─────────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        self._build_header()
        body = tk.Frame(self, bg=BG_DARK)
        body.pack(fill=tk.BOTH, expand=True)
        self._build_sidebar(body)
        self.content = tk.Frame(body, bg=BG_DARK)
        self.content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=16, pady=10)

    def _build_header(self):
        hdr = tk.Frame(self, bg=BG_CARD, height=60)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)

        logo = tk.Frame(hdr, bg=BG_CARD)
        logo.pack(side=tk.LEFT, padx=20, pady=10)
        tk.Label(logo, text="◈", font=("Courier New", 20, "bold"),
                 fg=ACCENT_CYAN, bg=BG_CARD).pack(side=tk.LEFT, padx=(0, 8))
        tk.Label(logo, text="FİNANSAL RİSK", font=("Courier New", 13, "bold"),
                 fg=TEXT_PRIMARY, bg=BG_CARD).pack(side=tk.LEFT)
        tk.Label(logo, text=" ANALİZ SİSTEMİ", font=("Courier New", 13),
                 fg=ACCENT_CYAN, bg=BG_CARD).pack(side=tk.LEFT)

        self.saat_lbl = tk.Label(hdr, text="", font=FONT_MONO,
                                 fg=TEXT_DIM, bg=BG_CARD)
        self.saat_lbl.pack(side=tk.RIGHT, padx=24)

        status = tk.Frame(hdr, bg=BG_CARD)
        status.pack(side=tk.RIGHT, padx=8)
        tk.Label(status, text="●", font=("Courier New", 10),
                 fg=ACCENT_GREEN, bg=BG_CARD).pack(side=tk.LEFT)
        tk.Label(status, text=" SİSTEM AKTİF", font=FONT_MONO,
                 fg=ACCENT_GREEN, bg=BG_CARD).pack(side=tk.LEFT)

        tk.Frame(self, bg=ACCENT_BLUE, height=2).pack(fill=tk.X)

    def _build_sidebar(self, parent):
        self.sidebar = tk.Frame(parent, bg=BG_CARD, width=210)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0), pady=10)
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="NAVİGASYON", font=FONT_MONO,
                 fg=TEXT_MUTED, bg=BG_CARD).pack(anchor="w", padx=16, pady=(16, 6))

        self._nav_btn("⬛  Dashboard",      self._goster_dashboard)
        self._nav_btn("＋  Müşteri Ekle",   self._goster_musteri_ekle)
        self._nav_btn("☰  Müşteri Listesi", self._goster_liste)
        self._nav_btn("⚑  Risk Analizi",    self._goster_risk)

        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(fill=tk.X, padx=12, pady=16)
        tk.Label(self.sidebar, text="HIZLI ÖZET", font=FONT_MONO,
                 fg=TEXT_MUTED, bg=BG_CARD).pack(anchor="w", padx=16, pady=(0, 8))

        # Mini stat etiketleri (dinamik güncellenebilir)
        self._sb_toplam  = self._mini_stat("Toplam Müşteri", "0")
        self._sb_yuksek  = self._mini_stat("Yüksek Riskli",  "0")
        self._sb_aciliyor= self._mini_stat("Açılıyor",       "0")
        self._guncelle_sidebar()

    def _nav_btn(self, text, cmd):
        btn = tk.Button(self.sidebar, text=text, font=FONT_BODY,
                        fg=TEXT_DIM, bg=BG_CARD,
                        activeforeground=NEON_CYAN, activebackground=BG_CARD2,
                        relief=tk.FLAT, anchor="w", padx=16, pady=8,
                        cursor="hand2", command=cmd)
        btn.pack(fill=tk.X, padx=4, pady=1)
        btn.bind("<Enter>", lambda e, b=btn: b.config(fg=NEON_CYAN, bg=BG_CARD2))
        btn.bind("<Leave>", lambda e, b=btn: b.config(fg=TEXT_DIM, bg=BG_CARD))

    def _mini_stat(self, label, val):
        f = tk.Frame(self.sidebar, bg=BG_CARD)
        f.pack(fill=tk.X, padx=12, pady=2)
        tk.Label(f, text=label, font=FONT_MONO,
                 fg=TEXT_MUTED, bg=BG_CARD).pack(side=tk.LEFT)
        lbl = tk.Label(f, text=val, font=FONT_SUBHEAD,
                       fg=NEON_CYAN, bg=BG_CARD)
        lbl.pack(side=tk.RIGHT)
        return lbl

    def _guncelle_sidebar(self):
        stats = self.servis.dashboard_verisi()["istatistik"]
        self._sb_toplam.config(text=str(stats["toplam"]))
        self._sb_yuksek.config(text=str(stats["yuksek"]))
        self._sb_aciliyor.config(text=str(stats["orta"]))

    # ─────────────────────────────────────────────────────────────────────────
    #  Yardımcılar
    # ─────────────────────────────────────────────────────────────────────────
    def _temizle(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _baslat_canli_saat(self):
        def guncelle():
            self.saat_lbl.config(
                text=datetime.now().strftime("  %d.%m.%Y  %H:%M:%S"))
            self.after(1000, guncelle)
        guncelle()

    def _sayfa_baslik(self, metin):
        f = tk.Frame(self.content, bg=BG_DARK)
        f.pack(fill=tk.X, pady=(0, 10))
        tk.Label(f, text=metin, font=FONT_HEADING,
                 fg=NEON_CYAN, bg=BG_DARK).pack(side=tk.LEFT)
        tk.Label(f, text=datetime.now().strftime(" — %d.%m.%Y"),
                 font=FONT_MONO, fg=TEXT_MUTED, bg=BG_DARK).pack(side=tk.LEFT, padx=6)
        tk.Frame(self.content, bg=ACCENT_BLUE, height=1).pack(fill=tk.X, pady=(0, 8))

    def _renk_seviye(self, seviye: str) -> str:
        return SEVİYE_RENK.get(seviye, ACCENT_GREEN)

    # ═════════════════════════════════════════════════════════════════════════
    #  DASHBOARD
    # ═════════════════════════════════════════════════════════════════════════
    def _goster_dashboard(self):
        self._temizle()
        self._sayfa_baslik("◈ GENEL DURUM TABLOSU")

        veri  = self.servis.dashboard_verisi()
        stats = veri["istatistik"]

        # ── KPI Kartları ────────────────────────────────────────────────────
        kpi_row = tk.Frame(self.content, bg=BG_DARK)
        kpi_row.pack(fill=tk.X, pady=(0, 12))

        self._kpi_kart(kpi_row, "TOPLAM MÜŞTERİ", str(stats["toplam"]),           ACCENT_BLUE,  "müşteri")
        self._kpi_kart(kpi_row, "YÜKSEK RİSK",    str(stats["yuksek"]),           ACCENT_RED,   "kişi")
        self._kpi_kart(kpi_row, "ORTA RİSK",       str(stats["orta"]),             ACCENT_AMBER, "kişi")
        self._kpi_kart(kpi_row, "NORMAL",          str(stats["normal"]),           ACCENT_GREEN, "kişi")
        self._kpi_kart(kpi_row, "ORT. BAKİYE",
                       f"{stats['ort_bakiye']:,.0f} ₺",                            ACCENT_CYAN,  "")

        # ── Alt bölüm ───────────────────────────────────────────────────────
        alt = tk.Frame(self.content, bg=BG_DARK)
        alt.pack(fill=tk.BOTH, expand=True)
        self._pasta_grafik(alt, stats["yuksek"], stats["orta"], stats["normal"])
        self._musteri_durum_listesi(alt, veri["musteriler"])

    def _kpi_kart(self, parent, baslik, deger, renk, birim):
        kart = tk.Frame(parent, bg=BG_CARD)
        kart.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)
        tk.Frame(kart, bg=renk, height=3).pack(fill=tk.X)
        tk.Label(kart, text=baslik, font=FONT_MONO,
                 fg=TEXT_MUTED, bg=BG_CARD).pack(anchor="w", padx=14, pady=(10, 2))
        tk.Label(kart, text=deger, font=FONT_MED,
                 fg=renk, bg=BG_CARD).pack(anchor="w", padx=14)
        tk.Label(kart, text=birim, font=FONT_MONO,
                 fg=TEXT_DIM, bg=BG_CARD).pack(anchor="w", padx=14, pady=(0, 12))

    def _pasta_grafik(self, parent, yuksek, orta, normal):
        frame = tk.Frame(parent, bg=BG_CARD)
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        tk.Label(frame, text="RİSK DAĞILIMI", font=FONT_HEADING,
                 fg=TEXT_PRIMARY, bg=BG_CARD).pack(anchor="w", padx=16, pady=(14, 0))

        c = tk.Canvas(frame, bg=BG_CARD, highlightthickness=0, width=280, height=240)
        c.pack(pady=10)

        toplam = yuksek + orta + normal or 1
        veriler = [
            (yuksek, ACCENT_RED,   "Yüksek Risk"),
            (orta,   ACCENT_AMBER, "Açılıyor"),
            (normal, ACCENT_GREEN, "Normal"),
        ]
        cx, cy, r = 120, 120, 85
        baslangic = -90
        for sayi, renk, _ in veriler:
            aci = (sayi / toplam) * 360
            if aci > 0:
                c.create_arc(cx - r, cy - r, cx + r, cy + r,
                             start=baslangic, extent=aci,
                             fill=renk, outline=BG_CARD, width=3)
            baslangic += aci

        c.create_oval(cx - 45, cy - 45, cx + 45, cy + 45,
                      fill=BG_CARD, outline=BG_CARD)
        c.create_text(cx, cy - 8, text=str(toplam),
                      font=FONT_MED, fill=TEXT_PRIMARY)
        c.create_text(cx, cy + 12, text="müşteri",
                      font=FONT_MONO, fill=TEXT_MUTED)

        leg = tk.Frame(frame, bg=BG_CARD)
        leg.pack(padx=16, pady=(0, 14))
        for sayi, renk, etiket in veriler:
            satir = tk.Frame(leg, bg=BG_CARD)
            satir.pack(fill=tk.X, pady=2)
            tk.Label(satir, text="██", font=FONT_MONO,
                     fg=renk, bg=BG_CARD).pack(side=tk.LEFT)
            tk.Label(satir, text=f" {etiket}", font=FONT_BODY,
                     fg=TEXT_DIM, bg=BG_CARD).pack(side=tk.LEFT)
            pct = sayi / toplam * 100
            tk.Label(satir, text=f"%{pct:.0f}", font=FONT_SUBHEAD,
                     fg=renk, bg=BG_CARD).pack(side=tk.RIGHT)

    def _musteri_durum_listesi(self, parent, musteriler: list[dict]):
        frame = tk.Frame(parent, bg=BG_CARD)
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 0))
        tk.Label(frame, text="MÜŞTERİ RİSK DURUMU", font=FONT_HEADING,
                 fg=TEXT_PRIMARY, bg=BG_CARD).pack(anchor="w", padx=16, pady=(14, 8))

        for kayit in musteriler:
            m    = kayit["musteri"]
            risk = kayit["risk"]
            renk = self._renk_seviye(risk["seviye"])
            satir = tk.Frame(frame, bg=BG_CARD2)
            satir.pack(fill=tk.X, padx=10, pady=3)
            tk.Label(satir, text="  " + m.ad, font=FONT_BODY,
                     fg=TEXT_PRIMARY, bg=BG_CARD2).pack(side=tk.LEFT, padx=(4, 0), pady=8)
            tk.Label(satir, text=f"Skor: {risk['skor']}",
                     font=FONT_MONO, fg=TEXT_DIM, bg=BG_CARD2).pack(side=tk.LEFT, padx=12)
            tk.Label(satir, text=f"  {risk['seviye']}  ", font=FONT_SUBHEAD,
                     fg=renk, bg=BG_CARD2).pack(side=tk.RIGHT, padx=8)

    # ═════════════════════════════════════════════════════════════════════════
    #  MÜŞTERİ EKLE
    # ═════════════════════════════════════════════════════════════════════════
    def _goster_musteri_ekle(self):
        self._temizle()
        self._sayfa_baslik("＋ YENİ MÜŞTERİ EKLE")

        form_wrap = tk.Frame(self.content, bg=BG_CARD)
        form_wrap.pack(fill=tk.BOTH, expand=True, pady=4)

        ic = tk.Frame(form_wrap, bg=BG_CARD)
        ic.pack(pady=20, padx=30, anchor="nw")

        alanlar = [
            ("Müşteri Adı Soyadı",   "text",   "Örn: Ahmet Yılmaz"),
            ("Bakiye (₺)",           "number", "Örn: 85000"),
            ("Gecikme Süresi (gün)", "number", "Örn: 15"),
            ("Tahsilat Oranı (%)",   "number", "0-100 arası"),
            ("Sektör",               "text",   "Örn: İnşaat, Tekstil..."),
        ]

        self.form_vars: dict[str, tk.StringVar] = {}

        for etiket, _, placeholder in alanlar:
            satir = tk.Frame(ic, bg=BG_CARD)
            satir.pack(fill=tk.X, pady=8)
            tk.Label(satir, text=etiket, font=FONT_SUBHEAD,
                     fg=TEXT_DIM, bg=BG_CARD, width=24, anchor="w").pack(side=tk.LEFT)
            var = tk.StringVar()
            self.form_vars[etiket] = var
            entry = tk.Entry(satir, textvariable=var, font=FONT_BODY,
                             bg=BG_CARD2, fg=TEXT_PRIMARY,
                             insertbackground=NEON_CYAN, relief=tk.FLAT, width=30,
                             highlightthickness=1, highlightbackground=BORDER,
                             highlightcolor=ACCENT_CYAN)
            entry.pack(side=tk.LEFT, ipady=8, padx=(0, 8))
            tk.Label(satir, text=placeholder, font=FONT_MONO,
                     fg=TEXT_MUTED, bg=BG_CARD).pack(side=tk.LEFT)

        # Butonlar
        btn_row = tk.Frame(ic, bg=BG_CARD)
        btn_row.pack(fill=tk.X, pady=20)

        tk.Button(btn_row, text="  ✓  MÜŞTERİYİ KAYDET  ",
                  font=FONT_HEADING, fg=BG_DARK, bg=ACCENT_CYAN,
                  activebackground=NEON_CYAN, activeforeground=BG_DARK,
                  relief=tk.FLAT, padx=24, pady=10, cursor="hand2",
                  command=self._kaydet_musteri).pack(side=tk.LEFT)

        tk.Button(btn_row, text="  ↺  Temizle  ",
                  font=FONT_BODY, fg=TEXT_DIM, bg=BG_CARD2,
                  activebackground=BG_CARD, activeforeground=TEXT_PRIMARY,
                  relief=tk.FLAT, padx=16, pady=10, cursor="hand2",
                  command=lambda: [v.set("") for v in self.form_vars.values()]).pack(
            side=tk.LEFT, padx=8)

        # Canlı önizleme
        self._canli_onizleme(form_wrap)

    def _canli_onizleme(self, parent):
        frame = tk.Frame(parent, bg=BG_CARD2, width=280)
        frame.pack(side=tk.RIGHT, fill=tk.Y, padx=20, pady=20)
        frame.pack_propagate(False)

        tk.Label(frame, text="CANLI ÖNIZLEME", font=FONT_MONO,
                 fg=TEXT_MUTED, bg=BG_CARD2).pack(pady=(16, 8))
        tk.Frame(frame, bg=BORDER, height=1).pack(fill=tk.X, padx=12, pady=4)

        self.onizleme_skor   = tk.Label(frame, text="—", font=FONT_BIG,
                                        fg=ACCENT_BLUE, bg=BG_CARD2)
        self.onizleme_skor.pack(pady=(16, 4))
        tk.Label(frame, text="Risk Skoru", font=FONT_MONO,
                 fg=TEXT_MUTED, bg=BG_CARD2).pack()

        self.onizleme_seviye = tk.Label(frame, text="GİRİŞ BEKLİYOR",
                                        font=FONT_HEADING, fg=TEXT_DIM, bg=BG_CARD2)
        self.onizleme_seviye.pack(pady=12)

        self.onizleme_notlar = tk.Label(frame, text="", font=FONT_MONO,
                                        fg=TEXT_MUTED, bg=BG_CARD2,
                                        wraplength=240, justify=tk.LEFT)
        self.onizleme_notlar.pack(padx=12, pady=4)

        def guncelle(*_):
            try:
                bakiye   = float(self.form_vars.get("Bakiye (₺)", tk.StringVar()).get() or 0)
                gecikme  = int(float(self.form_vars.get("Gecikme Süresi (gün)", tk.StringVar()).get() or 0))
                tahsilat = float(self.form_vars.get("Tahsilat Oranı (%)", tk.StringVar()).get() or 100)
                # ── Backend çağrısı ──────────────────────────────────────────
                risk = self.servis.risk_onizle(bakiye, gecikme, tahsilat)
                renk = self._renk_seviye(risk["seviye"])
                self.onizleme_skor.config(text=str(risk["skor"]), fg=renk)
                self.onizleme_seviye.config(text=risk["seviye"], fg=renk)
                self.onizleme_notlar.config(
                    text="\n".join(risk["aciklama"]) if risk["aciklama"] else "✓ Tüm kriterler normal"
                )
            except Exception:
                pass

        for var in self.form_vars.values():
            var.trace_add("write", guncelle)

    def _kaydet_musteri(self):
        try:
            ad       = self.form_vars["Müşteri Adı Soyadı"].get()
            bakiye   = float(self.form_vars["Bakiye (₺)"].get())
            gecikme  = int(float(self.form_vars["Gecikme Süresi (gün)"].get()))
            tahsilat = float(self.form_vars["Tahsilat Oranı (%)"].get())
            sektor   = self.form_vars["Sektör"].get()
            # ── Backend çağrısı ──────────────────────────────────────────────
            sonuc  = self.servis.musteri_ekle(ad, bakiye, gecikme, tahsilat, sektor)
            m      = sonuc["musteri"]
            risk   = sonuc["risk"]
        except (ValueError, KeyError) as e:
            messagebox.showerror("Hata", str(e))
            return

        messagebox.showinfo(
            "Başarılı",
            f"✓ {m.ad} başarıyla eklendi!\n\nRisk Seviyesi: {risk['seviye']}\nID: {m.id}"
        )
        self._guncelle_sidebar()
        self._goster_dashboard()

    # ═════════════════════════════════════════════════════════════════════════
    #  MÜŞTERİ LİSTESİ
    # ═════════════════════════════════════════════════════════════════════════
    def _goster_liste(self):
        self._temizle()
        self._sayfa_baslik("☰ MÜŞTERİ LİSTESİ")

        # Arama
        ara_frame = tk.Frame(self.content, bg=BG_DARK)
        ara_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(ara_frame, text="Ara:", font=FONT_BODY,
                 fg=TEXT_DIM, bg=BG_DARK).pack(side=tk.LEFT)
        self.ara_var = tk.StringVar()
        tk.Entry(ara_frame, textvariable=self.ara_var, font=FONT_BODY,
                 bg=BG_CARD, fg=TEXT_PRIMARY, relief=tk.FLAT,
                 insertbackground=NEON_CYAN, width=30,
                 highlightthickness=1, highlightbackground=BORDER,
                 highlightcolor=ACCENT_CYAN).pack(side=tk.LEFT, padx=8, ipady=6)

        # Tablo
        tablo_frame = tk.Frame(self.content, bg=BG_CARD)
        tablo_frame.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Dark.Treeview",
                        background=BG_CARD2, foreground=TEXT_PRIMARY,
                        fieldbackground=BG_CARD2, rowheight=36, font=FONT_BODY)
        style.configure("Dark.Treeview.Heading",
                        background=BG_CARD, foreground=NEON_CYAN,
                        font=FONT_SUBHEAD, relief=tk.FLAT)
        style.map("Dark.Treeview",
                  background=[("selected", ACCENT_BLUE)],
                  foreground=[("selected", TEXT_PRIMARY)])

        kolonlar = ("ID", "Ad Soyad", "Bakiye", "Gecikme", "Tahsilat", "Sektör", "Durum")
        self.tree = ttk.Treeview(tablo_frame, columns=kolonlar,
                                 show="headings", style="Dark.Treeview")
        gen = {"ID": 60, "Ad Soyad": 160, "Bakiye": 120, "Gecikme": 100,
               "Tahsilat": 110, "Sektör": 110, "Durum": 130}
        for k in kolonlar:
            self.tree.heading(k, text=k)
            self.tree.column(k, width=gen[k], anchor="center")

        sb_scroll = ttk.Scrollbar(tablo_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb_scroll.set)
        sb_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        def filtrele(*_):
            for item in self.tree.get_children():
                self.tree.delete(item)
            # ── Backend çağrısı ──────────────────────────────────────────────
            for kayit in self.servis.musteri_listesi(self.ara_var.get()):
                m    = kayit["musteri"]
                risk = kayit["risk"]
                self.tree.insert("", tk.END, iid=m.id, values=(
                    m.id, m.ad,
                    f"{m.bakiye:,.0f} ₺",
                    f"{m.gecikme} gün",
                    f"%{m.tahsilat:.0f}",
                    m.sektor,
                    risk["seviye"]
                ))

        self.ara_var.trace_add("write", filtrele)
        filtrele()

        # Alt buton satırı
        btn_row = tk.Frame(self.content, bg=BG_DARK)
        btn_row.pack(fill=tk.X, pady=10)

        # Analiz butonu
        tk.Button(btn_row, text="▶  Seçili Müşteriyi Analiz Et",
                  font=FONT_SUBHEAD, fg=BG_DARK, bg=ACCENT_CYAN,
                  activebackground=NEON_CYAN, activeforeground=BG_DARK,
                  relief=tk.FLAT, padx=20, pady=8, cursor="hand2",
                  command=self._analiz_secili).pack(side=tk.RIGHT, padx=4)

        # ── Silme butonu ─────────────────────────────────────────────────────
        tk.Button(btn_row, text="🗑  Seçili Müşteriyi Sil",
                  font=FONT_SUBHEAD, fg=TEXT_PRIMARY, bg=ACCENT_RED,
                  activebackground="#DC2626", activeforeground=TEXT_PRIMARY,
                  relief=tk.FLAT, padx=20, pady=8, cursor="hand2",
                  command=lambda: self._musteri_sil(filtrele)).pack(side=tk.RIGHT, padx=4)

    def _musteri_sil(self, yenile_fn=None):
        secim = self.tree.selection()
        if not secim:
            messagebox.showwarning("Uyarı", "Lütfen silmek istediğiniz müşteriyi seçin.")
            return

        musteri_id = secim[0]          # iid = musteri ID
        m = self.servis.depo.id_ile_getir(musteri_id)
        if m is None:
            return

        onay = messagebox.askyesno(
            "Silme Onayı",
            f"'{m.ad}' adlı müşteriyi silmek istediğinizden emin misiniz?\n\n"
            f"Bu işlem geri alınamaz.",
            icon="warning"
        )
        if not onay:
            return

        try:
            # ── Backend çağrısı ──────────────────────────────────────────────
            silinen = self.servis.musteri_sil(musteri_id)
            messagebox.showinfo("Başarılı", f"'{silinen.ad}' başarıyla silindi.")
        except KeyError as e:
            messagebox.showerror("Hata", str(e))
            return

        self._guncelle_sidebar()
        if yenile_fn:
            yenile_fn()

    def _analiz_secili(self):
        secim = self.tree.selection()
        if not secim:
            messagebox.showwarning("Uyarı", "Lütfen bir müşteri seçin.")
            return
        self._secili_musteri_id = secim[0]
        self._goster_risk()

    # ═════════════════════════════════════════════════════════════════════════
    #  RİSK ANALİZİ
    # ═════════════════════════════════════════════════════════════════════════
    def _goster_risk(self):
        self._temizle()
        self._sayfa_baslik("⚑ RİSK ANALİZİ")

        if self._secili_musteri_id is None:
            # Müşteri seçim arayüzü
            sec_frame = tk.Frame(self.content, bg=BG_CARD)
            sec_frame.pack(fill=tk.X, pady=8)
            tk.Label(sec_frame, text="Analiz edilecek müşteri seçin:",
                     font=FONT_SUBHEAD, fg=TEXT_DIM, bg=BG_CARD).pack(
                side=tk.LEFT, padx=12, pady=12)

            self.secim_var = tk.StringVar()
            # ── Backend çağrısı ──────────────────────────────────────────────
            adlar = [k["musteri"].ad for k in self.servis.musteri_listesi()]
            combo = ttk.Combobox(sec_frame, textvariable=self.secim_var,
                                 values=adlar, font=FONT_BODY,
                                 width=28, state="readonly")
            combo.pack(side=tk.LEFT, padx=8)

            tk.Button(sec_frame, text="  Analiz Et  ",
                      font=FONT_SUBHEAD, fg=BG_DARK, bg=ACCENT_CYAN,
                      relief=tk.FLAT, padx=12, pady=6, cursor="hand2",
                      command=self._sec_ve_analiz).pack(side=tk.LEFT, padx=8)
            return

        # Doğrudan detay göster
        musteri_id = self._secili_musteri_id
        self._secili_musteri_id = None
        try:
            # ── Backend çağrısı ──────────────────────────────────────────────
            kayit = self.servis.musteri_risk_detay(musteri_id)
            self._goster_risk_detay(kayit["musteri"], kayit["risk"])
        except KeyError:
            messagebox.showerror("Hata", "Müşteri bulunamadı.")

    def _sec_ve_analiz(self):
        ad = self.secim_var.get()
        if not ad:
            return
        # ── Backend çağrısı ──────────────────────────────────────────────────
        for kayit in self.servis.musteri_listesi():
            if kayit["musteri"].ad == ad:
                self._goster_risk_detay(kayit["musteri"], kayit["risk"])
                return

    def _goster_risk_detay(self, m, risk: dict):
        renk = self._renk_seviye(risk["seviye"])

        # Üst banner
        banner = tk.Frame(self.content, bg=renk)
        banner.pack(fill=tk.X, pady=(0, 12))
        tk.Label(banner,
                 text=f"  {m.ad}  —  {risk['seviye']}  —  Skor: {risk['skor']}/100  ",
                 font=FONT_HEADING, fg=BG_DARK, bg=renk).pack(pady=10)

        cols = tk.Frame(self.content, bg=BG_DARK)
        cols.pack(fill=tk.BOTH, expand=True)

        # Sol: Finansal Bilgiler
        sol = tk.Frame(cols, bg=BG_CARD)
        sol.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        tk.Label(sol, text="FİNANSAL BİLGİLER", font=FONT_HEADING,
                 fg=TEXT_PRIMARY, bg=BG_CARD).pack(anchor="w", padx=16, pady=(14, 6))
        tk.Frame(sol, bg=BORDER, height=1).pack(fill=tk.X, padx=12)

        bilgiler = [
            ("Müşteri ID",     m.id,                   NEON_CYAN),
            ("Ad Soyad",       m.ad,                   TEXT_PRIMARY),
            ("Sektör",         m.sektor,               TEXT_PRIMARY),
            ("Bakiye",         f"{m.bakiye:,.0f} ₺",   ACCENT_GREEN if m.bakiye >= 75000 else ACCENT_RED),
            ("Gecikme",        f"{m.gecikme} gün",     ACCENT_GREEN if m.gecikme <= 20 else
                                                       (ACCENT_AMBER if m.gecikme <= 30 else ACCENT_RED)),
            ("Tahsilat Oranı", f"%{m.tahsilat:.0f}",  ACCENT_GREEN if m.tahsilat >= 70 else ACCENT_AMBER),
            ("Kayıt Tarihi",   m.tarih,               TEXT_DIM),
        ]

        for etiket, deger, clr in bilgiler:
            satir = tk.Frame(sol, bg=BG_CARD)
            satir.pack(fill=tk.X, padx=16, pady=5)
            tk.Label(satir, text=etiket, font=FONT_BODY,
                     fg=TEXT_MUTED, bg=BG_CARD, width=18, anchor="w").pack(side=tk.LEFT)
            tk.Label(satir, text=deger, font=FONT_SUBHEAD,
                     fg=clr, bg=BG_CARD).pack(side=tk.LEFT)

        # Sağ: Skor & Öneriler
        sag = tk.Frame(cols, bg=BG_CARD)
        sag.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 0))
        tk.Label(sag, text="RİSK SKORU", font=FONT_HEADING,
                 fg=TEXT_PRIMARY, bg=BG_CARD).pack(anchor="w", padx=16, pady=(14, 4))

        tk.Label(sag, text=str(risk["skor"]), font=FONT_BIG,
                 fg=renk, bg=BG_CARD).pack(pady=8)

        bar = tk.Canvas(sag, bg=BG_CARD, highlightthickness=0, height=20, width=260)
        bar.pack(padx=16, pady=(0, 8))
        bar.create_rectangle(0, 6, 260, 14, fill=BG_CARD2, outline="")
        bar.create_rectangle(0, 6, int(risk["skor"] / 100 * 260), 14,
                             fill=renk, outline="")

        tk.Frame(sag, bg=BORDER, height=1).pack(fill=tk.X, padx=12, pady=4)
        tk.Label(sag, text="UYARILAR & ÖNERİLER", font=FONT_HEADING,
                 fg=TEXT_PRIMARY, bg=BG_CARD).pack(anchor="w", padx=16, pady=(4, 4))

        if risk["aciklama"]:
            for not_ in risk["aciklama"]:
                tk.Label(sag, text=not_, font=FONT_BODY, fg=ACCENT_AMBER,
                         bg=BG_CARD, anchor="w", wraplength=320,
                         justify=tk.LEFT).pack(anchor="w", padx=16, pady=3)
        else:
            tk.Label(sag, text="✓ Tüm finansal kriterler normal seviyede.",
                     font=FONT_BODY, fg=ACCENT_GREEN, bg=BG_CARD).pack(
                anchor="w", padx=16, pady=6)

        tk.Frame(sag, bg=BORDER, height=1).pack(fill=tk.X, padx=12, pady=8)
        tk.Label(sag, text="SİSTEM ÖNERİSİ", font=FONT_SUBHEAD,
                 fg=TEXT_MUTED, bg=BG_CARD).pack(anchor="w", padx=16)

        oneri_map = {
            RiskSeviyesi.YÜKSEK: "Acil müdahale gereklidir. Müşteri ile derhal iletişime "
                                  "geçilmeli, tahsilat planı oluşturulmalı.",
            RiskSeviyesi.ORTA:   "Yakın takip gereklidir. Gecikme artışı izlenmeli, "
                                  "önleyici adımlar atılmalı.",
            RiskSeviyesi.NORMAL: "Standart takip yeterlidir. Periyodik kontrol sürdürülmeli.",
        }
        tk.Label(sag, text=oneri_map.get(risk["seviye"], ""),
                 font=FONT_BODY, fg=TEXT_DIM, bg=BG_CARD,
                 wraplength=300, justify=tk.LEFT).pack(anchor="w", padx=16, pady=6)

        # ── Silme butonu (detay sayfasında da erişilebilir) ──────────────────
        tk.Frame(sag, bg=BORDER, height=1).pack(fill=tk.X, padx=12, pady=8)
        tk.Button(sag, text="🗑  Bu Müşteriyi Sil",
                  font=FONT_SUBHEAD, fg=TEXT_PRIMARY, bg=ACCENT_RED,
                  activebackground="#DC2626", activeforeground=TEXT_PRIMARY,
                  relief=tk.FLAT, padx=16, pady=6, cursor="hand2",
                  command=lambda mid=m.id: self._musteri_sil_ve_yonlendir(mid)
                  ).pack(anchor="w", padx=16, pady=(0, 14))

    def _musteri_sil_ve_yonlendir(self, musteri_id: str):
        """Detay sayfasından silme; başarılıysa dashboard'a döner."""
        m = self.servis.depo.id_ile_getir(musteri_id)
        if not m:
            return
        onay = messagebox.askyesno(
            "Silme Onayı",
            f"'{m.ad}' adlı müşteriyi silmek istediğinizden emin misiniz?\n\n"
            f"Bu işlem geri alınamaz.",
            icon="warning"
        )
        if not onay:
            return
        try:
            silinen = self.servis.musteri_sil(musteri_id)
            messagebox.showinfo("Başarılı", f"'{silinen.ad}' başarıyla silindi.")
        except KeyError as e:
            messagebox.showerror("Hata", str(e))
            return
        self._guncelle_sidebar()
        self._goster_dashboard()


# ─── Giriş ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = FinansalRiskApp()
    app.mainloop()