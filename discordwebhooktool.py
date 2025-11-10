
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import time
import random
import string
import requests
import json
import csv
import os
from datetime import datetime

THEMES = {
    'dark': {'BG': "#121214", 'FG': "#e6edf3", 'INPUT_BG': "#1e1f22", 'BTN_BG': "#27292c", 'LOG_BG': "#0f1112", 'WARN_COLOR': "#ffb86b"}
}

BG = THEMES['dark']['BG']
FG = THEMES['dark']['FG']
INPUT_BG = THEMES['dark']['INPUT_BG']
BTN_BG = THEMES['dark']['BTN_BG']
LOG_BG = THEMES['dark']['LOG_BG']
WARN_COLOR = THEMES['dark']['WARN_COLOR']

def now_ts():
    return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

def gen_random_string(length=6, charset=string.ascii_letters + string.digits):
    return ''.join(random.choice(charset) for _ in range(length))

def generate_fake_gift(length=16, charset=string.ascii_letters + string.digits):
    return 'discord.gift/' + ''.join(random.choice(charset) for _ in range(length))

def generate_fake_invite(length=6, charset=string.ascii_letters + string.digits):
    return 'discord.gg/' + ''.join(random.choice(charset) for _ in range(length))

def send_webhook_with_backoff(url, payload, max_retries=5, base_backoff=1.0, timeout=10):
    attempt = 0
    while attempt <= max_retries:
        try:
            res = requests.post(url, json=payload, timeout=timeout)
            status = res.status_code
            text = res.text
            if status == 429:
                retry_after = None
                try:
                    j = res.json()
                    retry_after = j.get('retry_after')
                except Exception:
                    pass
                wait = retry_after if retry_after is not None else (base_backoff * (2 ** attempt))
                attempt += 1
                time.sleep(wait)
                continue
            return status, text
        except Exception as e:
            return None, str(e)
    return None, f'Exceeded {max_retries} retries due to rate limit.'

def apply_theme(root, theme_name):
    theme = THEMES.get(theme_name, THEMES['dark'])
    root.configure(bg=theme['BG'])
    global BG, FG, INPUT_BG, BTN_BG, LOG_BG, WARN_COLOR
    BG, FG, INPUT_BG, BTN_BG, LOG_BG, WARN_COLOR = theme['BG'], theme['FG'], theme['INPUT_BG'], theme['BTN_BG'], theme['LOG_BG'], theme['WARN_COLOR']

class WebhookToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Discord Webhook Tool — Full')
        self.root.configure(bg=BG)
        self.stop_event = threading.Event()
        self.jobs = []
        self.logs = []
        self.profiles_dir = os.path.join(os.path.expanduser('~'), '.discord_webhook_tool')
        os.makedirs(self.profiles_dir, exist_ok=True)
        self.build_ui()

    def build_ui(self):
        pad = 8
        top = tk.Frame(self.root, bg=BG)
        top.pack(fill='x', padx=pad, pady=(pad,0))
        tk.Label(top, text='Webhook URL:', bg=BG, fg=FG).grid(row=0, column=0, sticky='w')
        self.webhook_var = tk.StringVar()
        self.webhook_entry = tk.Entry(top, textvariable=self.webhook_var, bg=INPUT_BG, fg=FG, insertbackground=FG)
        self.webhook_entry.grid(row=0, column=1, sticky='we', padx=(6,0))
        top.grid_columnconfigure(1, weight=1)
        self.validate_btn = tk.Button(top, text='Validate', bg=BTN_BG, fg=FG, command=self.validate_webhook)
        self.validate_btn.grid(row=0, column=2, padx=(6,0))

        mid = tk.Frame(self.root, bg=BG)
        mid.pack(fill='x', padx=pad, pady=(pad,0))
        tk.Label(mid, text='Mode:', bg=BG, fg=FG).grid(row=0, column=0, sticky='w')
        self.mode_var = tk.StringVar(value='normal')
        self.mode_combo = ttk.Combobox(mid, textvariable=self.mode_var,
                                       values=['normal','fake_gift','fake_invite','embed'], state='readonly')
        self.mode_combo.grid(row=0, column=1, sticky='we', padx=6)
        tk.Label(mid, text='Interval (s):', bg=BG, fg=FG).grid(row=0, column=2, sticky='w', padx=(8,0))
        self.interval_var = tk.DoubleVar(value=5.0)
        self.interval_spin = tk.Spinbox(mid, from_=0.5, to=3600, increment=0.5, textvariable=self.interval_var,
                                        bg=INPUT_BG, fg=FG, insertbackground=FG)
        self.interval_spin.grid(row=0, column=3, sticky='we', padx=(2,0))
        tk.Label(mid, text='Theme:', bg=BG, fg=FG).grid(row=0, column=4, sticky='w', padx=(8,0))
        self.theme_var = tk.StringVar(value='dark')
        self.theme_combo = ttk.Combobox(mid, textvariable=self.theme_var, values=list(THEMES.keys()), state='readonly', width=6)
        self.theme_combo.grid(row=0, column=5, sticky='we', padx=(2,0))
        self.theme_combo.bind('<<ComboboxSelected>>', lambda e: apply_theme(self.root, self.theme_var.get()))

        tk.Label(mid, text='Code Length:', bg=BG, fg=FG).grid(row=1, column=0, sticky='w', pady=(6,0))
        self.gift_length_var = tk.IntVar(value=16)
        self.gift_length_spin = tk.Spinbox(mid, from_=6, to=64, increment=1, textvariable=self.gift_length_var,
                                           bg=INPUT_BG, fg=FG, insertbackground=FG)
        self.gift_length_spin.grid(row=1, column=1, sticky='we', padx=6, pady=(6,0))
        tk.Label(mid, text='Charset:', bg=BG, fg=FG).grid(row=1, column=2, sticky='w', pady=(6,0))
        self.charset_var = tk.StringVar(value='alnum')
        self.charset_combo = ttk.Combobox(mid, textvariable=self.charset_var, values=['alnum','alpha','digits','custom'], state='readonly')
        self.charset_combo.grid(row=1, column=3, sticky='we', padx=(2,0), pady=(6,0))
        tk.Label(mid, text='Custom charset:', bg=BG, fg=FG).grid(row=2, column=0, sticky='w', pady=(6,0))
        self.custom_charset_var = tk.StringVar(value=string.ascii_letters + string.digits)
        self.custom_charset_entry = tk.Entry(mid, textvariable=self.custom_charset_var, bg=INPUT_BG, fg=FG, insertbackground=FG)
        self.custom_charset_entry.grid(row=2, column=1, columnspan=5, sticky='we', pady=(6,0))

        tk.Label(self.root, text='Message Template ({{random}}, {{time}}):', bg=BG, fg=FG).pack(anchor='w', padx=pad, pady=(pad,0))
        self.template_entry = tk.Entry(self.root, bg=INPUT_BG, fg=FG, insertbackground=FG)
        self.template_entry.insert(0,'Merhaba! Test: {{random}}')
        self.template_entry.pack(fill='x', padx=pad, pady=(2,0))

        emb_frame = tk.Frame(self.root, bg=BG)
        emb_frame.pack(fill='x', padx=pad, pady=(pad,0))
        tk.Label(emb_frame, text='Embed Title:', bg=BG, fg=FG).grid(row=0,column=0, sticky='w')
        self.embed_title = tk.Entry(emb_frame, bg=INPUT_BG, fg=FG, insertbackground=FG)
        self.embed_title.grid(row=0,column=1, sticky='we', padx=6)
        tk.Label(emb_frame, text='Embed Description:', bg=BG, fg=FG).grid(row=1,column=0, sticky='w')
        self.embed_desc = tk.Entry(emb_frame, bg=INPUT_BG, fg=FG, insertbackground=FG)
        self.embed_desc.grid(row=1,column=1, sticky='we', padx=6)
        emb_frame.grid_columnconfigure(1, weight=1)

        fields_frame = tk.Frame(self.root, bg=BG)
        fields_frame.pack(fill='x', padx=pad, pady=(6,0))
        tk.Label(fields_frame, text='Fields (Title:Value)', bg=BG, fg=FG).pack(anchor='w')
        self.embed_fields_text = tk.Entry(fields_frame, bg=INPUT_BG, fg=FG, insertbackground=FG)
        self.embed_fields_text.pack(fill='x')
        tk.Button(fields_frame, text='Preview Embed', bg=BTN_BG, fg=FG, command=self.preview_embed).pack(anchor='e', pady=(6,0))

        btn_frame = tk.Frame(self.root, bg=BG)
        btn_frame.pack(fill='x', padx=pad, pady=(pad,0))
        self.start_btn = tk.Button(btn_frame, text='Start', bg=BTN_BG, fg=FG, command=self.start)
        self.start_btn.pack(side='left')
        self.stop_btn = tk.Button(btn_frame, text='Stop', bg=BTN_BG, fg=FG, command=self.stop, state='disabled')
        self.stop_btn.pack(side='left', padx=(6,0))
        tk.Button(btn_frame, text='Send Once', bg=BTN_BG, fg=FG, command=self.send_once).pack(side='left', padx=(6,0))

        sched_frame = tk.Frame(self.root, bg=BG)
        sched_frame.pack(fill='x', padx=pad, pady=(pad,0))
        tk.Label(sched_frame, text='Scheduler (one-shot: ISO or now+Xs, recurring: every Xs):', bg=BG, fg=FG).pack(anchor='w')
        self.schedule_entry = tk.Entry(sched_frame, bg=INPUT_BG, fg=FG, insertbackground=FG)
        self.schedule_entry.pack(fill='x')
        tk.Button(sched_frame, text='Add Job', bg=BTN_BG, fg=FG, command=self.add_job).pack(anchor='e', pady=(6,0))

        prof_frame = tk.Frame(self.root, bg=BG)
        prof_frame.pack(fill='x', padx=pad, pady=(pad,0))
        tk.Button(prof_frame, text='Save Profile', bg=BTN_BG, fg=FG, command=self.save_profile).pack(side='left')
        tk.Button(prof_frame, text='Load Profile', bg=BTN_BG, fg=FG, command=self.load_profile).pack(side='left', padx=(6,0))
        tk.Button(prof_frame, text='Export Logs CSV', bg=BTN_BG, fg=FG, command=self.export_logs_csv).pack(side='left', padx=(6,0))

        lower = tk.PanedWindow(self.root, orient='horizontal', bg=BG)
        lower.pack(fill='both', expand=True, padx=pad, pady=(pad,pad))
        left = tk.Frame(lower, bg=BG)
        tk.Label(left, text='Embed Preview:', bg=BG, fg=FG).pack(anchor='w')
        self.preview_box = tk.Text(left, height=12, bg=LOG_BG, fg=FG, state='disabled')
        self.preview_box.pack(fill='both', expand=True)
        tk.Label(left, text='Scheduled Jobs:', bg=BG, fg=FG).pack(anchor='w', pady=(6,0))
        self.jobs_box = tk.Listbox(left, bg=INPUT_BG, fg=FG)
        self.jobs_box.pack(fill='x')
        right = tk.Frame(lower, bg=BG)
        tk.Label(right, text='Log:', bg=BG, fg=FG).pack(anchor='w')
        self.log_area = scrolledtext.ScrolledText(right, height=20, bg=LOG_BG, fg=FG, state='normal')
        self.log_area.pack(fill='both', expand=True)
        lower.add(left)
        lower.add(right)

        tk.Label(self.root, text='UYARI: Bu araç test amaçlıdır. Gerçek Nitro/Invite kodlarını denemek yasaktır.', bg=BG, fg=WARN_COLOR, wraplength=700).pack(fill='x', padx=pad, pady=(6,6))
        self.log('Uygulama hazır.')

    def log(self, text):
        entry = f'[{now_ts()}] {text}'
        self.log_area.insert('end', entry+'\n')
        self.log_area.see('end')
        self.logs.append({'ts': now_ts(), 'text': text})

    def validate_webhook(self):
        url = self.webhook_var.get().strip()
        if not url:
            messagebox.showwarning('Hata', 'Webhook URL girin')
            return
        self.log('Validating webhook...')
        def worker():
            try:
                res = requests.post(url, json={'content':'validation ping (tool)'}, timeout=10)
                code = res.status_code
                if code in (200,204):
                    self.log(f'Validation OK (HTTP {code})')
                    messagebox.showinfo('Doğrulandı', f'Webhook doğrulandı (HTTP {code})')
                else:
                    self.log(f'Validation returned HTTP {code}')
                    messagebox.showwarning('Doğrulama Hatası', f'Webhook test isteği HTTP {code}')
            except Exception as e:
                self.log(f'Validation error: {e}')
                messagebox.showerror('Hata', f'Webhook doğrulanamadı: {e}')
        threading.Thread(target=worker, daemon=True).start()

    def build_payload(self):
        mode = self.mode_var.get()
        if mode == 'normal':
            tpl = self.template_entry.get()
            content = tpl.replace('{{random}}', gen_random_string(8)).replace('{{time}}', now_ts())
            return {'content': content}
        elif mode == 'fake_gift':
            ln = int(self.gift_length_var.get())
            cs = self.get_charset()
            content = generate_fake_gift(ln, cs)
            return {'content': content}
        elif mode == 'fake_invite':
            ln = int(self.gift_length_var.get())
            cs = self.get_charset()
            content = generate_fake_invite(ln, cs)
            return {'content': content}
        else:  # embed
            embed = {}
            title = self.embed_title.get().strip()
            desc = self.embed_desc.get().strip()
            if title: embed['title']=title
            if desc: embed['description']=desc
            fields_raw = self.embed_fields_text.get().strip()
            embeds_fields=[]
            if fields_raw:
                parts=[p.strip() for p in fields_raw.split(';') if p.strip()]
                for p in parts:
                    if ':' in p:
                        t,v=p.split(':',1)
                        embeds_fields.append({'name':t.strip(),'value':v.strip(),'inline':False})
            if embeds_fields: embed['fields']=embeds_fields
            return {'embeds':[embed]} if embed else {'content':'(empty embed)'}

    def get_charset(self):
        cs_key = self.charset_var.get()
        if cs_key=='alnum': return string.ascii_letters+string.digits
        elif cs_key=='alpha': return string.ascii_letters
        elif cs_key=='digits': return string.digits
        else: return self.custom_charset_var.get() or (string.ascii_letters+string.digits)

    def preview_embed(self):
        payload=self.build_payload()
        self.preview_box.config(state='normal'); self.preview_box.delete('1.0','end')
        try:
            if 'embeds' in payload:
                e=payload['embeds'][0]
                self.preview_box.insert('end',f"Title: {e.get('title','')}\n")
                self.preview_box.insert('end',f"Description: {e.get('description','')}\n\n")
                for f in e.get('fields',[]): self.preview_box.insert('end',f"{f.get('name')}: {f.get('value')}\n")
            else: self.preview_box.insert('end',payload.get('content',''))
        except Exception as ex: self.preview_box.insert('end',f'Preview error: {ex}')
        self.preview_box.config(state='disabled')

    def send_once(self):
        url=self.webhook_var.get().strip()
        if not url: messagebox.showwarning('Hata','Webhook URL boş'); return
        payload=self.build_payload()
        self.log(f'Sending once: {payload}')
        threading.Thread(target=lambda: self._send_worker(url,payload), daemon=True).start()
    def _send_worker(self,url,payload):
        code,text=send_webhook_with_backoff(url,payload)
        if code is None: self.log(f'Send error: {text}')
        else: self.log(f'Sent HTTP {code}')


    def start(self):
        url=self.webhook_var.get().strip()
        if not url: messagebox.showwarning('Hata','Webhook URL girin'); return
        self.stop_event.clear()
        self.start_btn.config(state='disabled'); self.stop_btn.config(state='normal')
        self.log('Auto-sender started')
        threading.Thread(target=self._auto_loop, daemon=True).start()
    def stop(self):
        self.stop_event.set()
        self.start_btn.config(state='normal'); self.stop_btn.config(state='disabled')
        self.log('Auto-sender stopped')
    def _auto_loop(self):
        url=self.webhook_var.get().strip()
        interval=float(self.interval_var.get())
        while not self.stop_event.is_set():
            payload=self.build_payload()
            self.log(f'Auto sending: {payload}')
            code,text=send_webhook_with_backoff(url,payload)
            if code is None: self.log(f'Auto send error: {text}')
            else: self.log(f'Auto sent HTTP {code}')
            waited=0.0; step=0.25
            while waited<interval:
                if self.stop_event.is_set(): break
                time.sleep(step); waited+=step

    def add_job(self):
        spec=self.schedule_entry.get().strip()
        if not spec: messagebox.showwarning('Hata','Planlama belirtin'); return
        job={'spec':spec,'payload':self.build_payload(),'next_run':None}
        try:
            if spec.startswith('now+'):
                secs=float(spec.split('+',1)[1].rstrip('s'))
                job['next_run']=time.time()+secs; job['type']='oneshot'
            elif spec.startswith('every '):
                secs=float(spec.split(' ',1)[1].rstrip('s'))
                job['interval']=secs; job['next_run']=time.time()+secs; job['type']='recurring'
            else:
                dt=datetime.fromisoformat(spec)
                job['next_run']=dt.timestamp(); job['type']='oneshot'
        except Exception as e:
            messagebox.showerror('Hata',f'Planlama spec anlaşılamadı: {e}'); return
        self.jobs.append(job)
        self.jobs_box.insert('end',f"{job['type']} -> {spec}")
        self.log(f'Added job: {spec}')
        if len(self.jobs)==1: threading.Thread(target=self._scheduler_loop,daemon=True).start()
    def _scheduler_loop(self):
        self.log('Scheduler started')
        while any(job.get('next_run') for job in self.jobs):
            now_t=time.time()
            for job in list(self.jobs):
                nr=job.get('next_run')
                if nr and now_t>=nr:
                    self.log(f'Firing scheduled job: {job.get("spec")}')
                    threading.Thread(target=lambda p=job['payload']: send_webhook_with_backoff(self.webhook_var.get().strip(),p), daemon=True).start()
                    if job.get('type')=='recurring': job['next_run']=now_t+job.get('interval')
                    else:
                        try: idx=self.jobs.index(job); self.jobs.pop(idx); self.jobs_box.delete(idx)
                        except ValueError: pass
            time.sleep(0.5)
        self.log('Scheduler finished')


    def save_profile(self):
        profile={'webhook':self.webhook_var.get(),'mode':self.mode_var.get(),'interval':self.interval_var.get(),
                 'template':self.template_entry.get(),'gift_length':self.gift_length_var.get(),'charset':self.charset_var.get(),
                 'custom_charset':self.custom_charset_var.get(),'embed_title':self.embed_title.get(),'embed_desc':self.embed_desc.get(),
                 'embed_fields':self.embed_fields_text.get()}
        name=filedialog.asksaveasfilename(initialdir=self.profiles_dir,defaultextension='.json',filetypes=[('JSON','*.json')])
        if not name: return
        with open(name,'w',encoding='utf-8') as f: json.dump(profile,f,ensure_ascii=False,indent=2)
        self.log(f'Profile saved: {name}')
    def load_profile(self):
        name=filedialog.askopenfilename(initialdir=self.profiles_dir,filetypes=[('JSON','*.json')])
        if not name: return
        try:
            with open(name,'r',encoding='utf-8') as f: profile=json.load(f)
            self.webhook_var.set(profile.get('webhook',''))
            self.mode_var.set(profile.get('mode','normal'))
            self.interval_var.set(profile.get('interval',5.0))
            self.template_entry.delete(0,'end'); self.template_entry.insert(0,profile.get('template',''))
            self.gift_length_var.set(profile.get('gift_length',16))
            self.charset_var.set(profile.get('charset','alnum'))
            self.custom_charset_var.set(profile.get('custom_charset',string.ascii_letters+string.digits))
            self.embed_title.delete(0,'end'); self.embed_title.insert(0,profile.get('embed_title',''))
            self.embed_desc.delete(0,'end'); self.embed_desc.insert(0,profile.get('embed_desc',''))
            self.embed_fields_text.delete(0,'end'); self.embed_fields_text.insert(0,profile.get('embed_fields',''))
            self.log(f'Profile loaded: {name}')
        except Exception as e: messagebox.showerror('Hata',f'Profile yüklenemedi: {e}')


    def export_logs_csv(self):
        name=filedialog.asksaveasfilename(defaultextension='.csv',filetypes=[('CSV','*.csv')])
        if not name: return
        try:
            with open(name,'w',newline='',encoding='utf-8') as f:
                writer=csv.writer(f)
                writer.writerow(['timestamp','text'])
                for entry in self.logs: writer.writerow([entry['ts'],entry['text']])
            self.log(f'Logs exported: {name}')
        except Exception as e: messagebox.showerror('Hata',f'Logs export failed: {e}')


def main():
    root=tk.Tk()
    app=WebhookToolApp(root)
    root.geometry('900x700')
    root.mainloop()

if __name__=='__main__':
    main()
