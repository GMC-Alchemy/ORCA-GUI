"""
ORCA Input Builder (GUI)
------------------------
A Tkinter-based GUI tool for building ORCA quantum chemistry input files.

Features:
- Select job type, method, basis set, solvent.
- Configure charge, multiplicity, and resources.
- Toggle extra keywords (TightSCF, D3BJ, CPCM, etc.).
- Load or paste molecular coordinates (XYZ/PDB).
- Add custom ORCA input blocks.
- Live preview with copy, save, and template support.

Author: Gabriel Monteiro de Castro, Ph.D.
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

JOB_KEYWORDS = {
    'Single Point (SP)': 'SP',
    'Geometry Optimization (OPT)': 'Opt',
    'Vibrational Frequency (FREQ)': 'Freq',
    'OPT + FREQ': 'Opt Freq',
    'Excited States (TD-DFT)': 'TDDFT',
    'Scan': 'Opt Scan',
    'Transition State (TS)': 'OptTS',
    'Solvation': 'Opt CPCM',
    'Molecular Mechanics (MM)': 'MM',
    'QM/MM': 'QMMM'
}

COMMON_METHODS = ['B3LYP', 'PBE0', 'wB97X-D', 'PBE', 'M06-2X', 'HF', 'B97-D3']
COMMON_BASIS = ['def2-SVP', 'def2-TZVP', 'def2-QZVP', '6-31G*', '6-311G**', 'cc-pVDZ', 'cc-pVTZ']
SOLVENTS = ['Water', 'Methanol', 'Ethanol', 'Acetonitrile', 'Dichloromethane', 'Toluene']

class ORCAInputBuilder(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('GMC - ORCA Input Builder')
        self.geometry('1200x800')
        self.minsize(1000, 700)

        self.job_type = tk.StringVar(value='Single Point (SP)')
        self.method = tk.StringVar(value='B3LYP')
        self.basis = tk.StringVar(value='def2-SVP')
        self.charge = tk.StringVar(value='0')
        self.mult = tk.StringVar(value='1')
        self.custom_keywords = tk.StringVar(value='')
        self.solvent = tk.StringVar(value=SOLVENTS[0])

        self.tightscf = tk.IntVar(value=1)
        self.d3bj = tk.IntVar(value=0)
        self.rij = tk.IntVar(value=0)
        self.grid5 = tk.IntVar(value=0)
        self.cpcm = tk.IntVar(value=0)
        self.verytightscf = tk.IntVar(value=0)
        self.slowconv = tk.IntVar(value=0)
        self.defgrid3 = tk.IntVar(value=0)
        self.defgridx = tk.IntVar(value=0)

        self.maxcore = tk.StringVar(value='2000')
        self.nprocs = tk.StringVar(value='4')
        self.auto_format_coords = tk.IntVar(value=1)

        self.custom_blocks = tk.StringVar(value='')

        self.preview_locked = tk.BooleanVar(value=True)
        self.word_wrap = tk.BooleanVar(value=False)

        self.create_widgets()
        self.bind_events()
        self.update_preview()

    def create_widgets(self):
        frm_top = ttk.Frame(self)
        frm_top.pack(side=tk.TOP, fill=tk.X, padx=8, pady=8)

        job_frame = ttk.LabelFrame(frm_top, text='Job Settings')
        job_frame.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=6)

        ttk.Label(job_frame, text='Job Type:').grid(row=0, column=0, sticky='w')
        ttk.OptionMenu(job_frame, self.job_type, self.job_type.get(), *JOB_KEYWORDS.keys(), command=lambda _: self.update_preview()).grid(row=0, column=1, sticky='ew', padx=4, pady=2)

        ttk.Label(job_frame, text='Method:').grid(row=1, column=0, sticky='w')
        ttk.OptionMenu(job_frame, self.method, self.method.get(), *COMMON_METHODS, command=lambda _: self.update_preview()).grid(row=1, column=1, sticky='ew', padx=4, pady=2)

        ttk.Label(job_frame, text='Basis Set:').grid(row=2, column=0, sticky='w')
        ttk.OptionMenu(job_frame, self.basis, self.basis.get(), *COMMON_BASIS, command=lambda _: self.update_preview()).grid(row=2, column=1, sticky='ew', padx=4, pady=2)

        ttk.Label(job_frame, text='Charge:').grid(row=3, column=0, sticky='w')
        ttk.Entry(job_frame, textvariable=self.charge, width=6).grid(row=3, column=1, sticky='w', padx=4, pady=2)

        ttk.Label(job_frame, text='Multiplicity:').grid(row=4, column=0, sticky='w')
        ttk.Entry(job_frame, textvariable=self.mult, width=6).grid(row=4, column=1, sticky='w', padx=4, pady=2)

        ttk.Label(job_frame, text='Solvent:').grid(row=5, column=0, sticky='w')
        ttk.OptionMenu(job_frame, self.solvent, self.solvent.get(), *SOLVENTS, command=lambda _: self.update_preview()).grid(row=5, column=1, sticky='ew', padx=4, pady=2)

        extras_frame = ttk.LabelFrame(frm_top, text='Extras / Corrections')
        extras_frame.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=6)

        extras = [
            ('TightSCF', self.tightscf),
            ('D3BJ', self.d3bj),
            ('RIJCOSX', self.rij),
            ('Grid5', self.grid5),
            ('CPCM', self.cpcm),
            ('VeryTightSCF', self.verytightscf),
            ('SlowConv', self.slowconv),
            ('DefGrid3', self.defgrid3),
            ('DefGridX', self.defgridx),
        ]
        for i, (label, var) in enumerate(extras):
            ttk.Checkbutton(extras_frame, text=label, variable=var, command=self.update_preview).grid(row=i, column=0, sticky='w')

        ttk.Label(extras_frame, text='Custom keywords:').grid(row=len(extras), column=0, sticky='w', pady=(6,0))
        ttk.Entry(extras_frame, textvariable=self.custom_keywords, width=25).grid(row=len(extras)+1, column=0, sticky='ew', pady=2)

        res_frame = ttk.LabelFrame(frm_top, text='Resources')
        res_frame.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=6)

        ttk.Label(res_frame, text='MaxCore (MB):').grid(row=0, column=0, sticky='w')
        ttk.Entry(res_frame, textvariable=self.maxcore, width=8).grid(row=0, column=1, sticky='w', padx=4)

        ttk.Label(res_frame, text='Processors:').grid(row=1, column=0, sticky='w')
        ttk.Entry(res_frame, textvariable=self.nprocs, width=8).grid(row=1, column=1, sticky='w', padx=4)

        ttk.Checkbutton(res_frame, text='Auto-format coordinates', variable=self.auto_format_coords).grid(row=2, column=0, columnspan=2, sticky='w')

        mid_frame = ttk.Frame(self)
        mid_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=4)

        coords_frame = ttk.LabelFrame(mid_frame, text='Molecular Coordinates (XYZ)')
        coords_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=6)

        coord_btn_frame = ttk.Frame(coords_frame)
        coord_btn_frame.pack(side=tk.TOP, fill=tk.X)
        ttk.Button(coord_btn_frame, text='Load', command=self.load_coords).pack(side=tk.LEFT, padx=4, pady=4)
        ttk.Button(coord_btn_frame, text='Clear', command=self.clear_coords).pack(side=tk.LEFT, padx=4, pady=4)

        self.coords_text = tk.Text(coords_frame, wrap='none')
        self.coords_text.pack(fill=tk.BOTH, expand=True)

        coord_vsb = ttk.Scrollbar(coords_frame, orient='vertical', command=self.coords_text.yview)
        coord_vsb.pack(side=tk.RIGHT, fill='y')
        self.coords_text.config(yscrollcommand=coord_vsb.set)

        cb_frame = ttk.LabelFrame(mid_frame, text='Custom Blocks (%... end)')
        cb_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=6)

        self.cb_text = tk.Text(cb_frame, wrap='none')
        self.cb_text.pack(fill=tk.BOTH, expand=True)
        self.cb_text.insert('1.0', self.custom_blocks.get())

        cb_vsb = ttk.Scrollbar(cb_frame, orient='vertical', command=self.cb_text.yview)
        cb_vsb.pack(side=tk.RIGHT, fill='y')
        self.cb_text.config(yscrollcommand=cb_vsb.set)

        preview_frame = ttk.LabelFrame(self, text='Live Preview')
        preview_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=8, pady=8)

        btn_frame = ttk.Frame(preview_frame)
        btn_frame.pack(side=tk.TOP, fill=tk.X)
        ttk.Button(btn_frame, text='Lock/Unlock Preview', command=self.toggle_preview_lock).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text='Copy to Clipboard', command=self.copy_preview).pack(side=tk.LEFT, padx=4)
        ttk.Checkbutton(btn_frame, text='Word Wrap', variable=self.word_wrap, command=self.toggle_wrap).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text='Load Template', command=self.load_template).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text='Save Template', command=self.save_template).pack(side=tk.LEFT, padx=4)

        self.out_name = tk.StringVar(value='orca_input.inp')
        ttk.Label(btn_frame, text='Filename:').pack(side=tk.LEFT, padx=4)
        ttk.Entry(btn_frame, textvariable=self.out_name, width=25).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text='Save Input', command=self.save_input).pack(side=tk.LEFT, padx=4)

        self.preview_text = tk.Text(preview_frame, wrap='none')
        self.preview_text.pack(fill=tk.BOTH, expand=True)

        preview_vsb = ttk.Scrollbar(preview_frame, orient='vertical', command=self.preview_text.yview)
        preview_vsb.pack(side=tk.RIGHT, fill='y')
        self.preview_text.config(yscrollcommand=preview_vsb.set)

    def bind_events(self):
        self.coords_text.bind('<KeyRelease>', lambda e: self.update_preview_if_locked())
        self.cb_text.bind('<KeyRelease>', lambda e: self.update_preview_if_locked())
        for var in (self.job_type, self.method, self.basis, self.charge, self.mult, self.custom_keywords,
                    self.solvent, self.maxcore, self.nprocs):
            var.trace_add('write', lambda *args: self.update_preview_if_locked())

    def toggle_preview_lock(self):
        self.preview_locked.set(not self.preview_locked.get())
        messagebox.showinfo('Preview Lock', f"Preview is now {'locked' if self.preview_locked.get() else 'unlocked'}.")

    def toggle_wrap(self):
        self.preview_text.config(wrap='word' if self.word_wrap.get() else 'none')

    def copy_preview(self):
        self.clipboard_clear()
        self.clipboard_append(self.preview_text.get('1.0', tk.END))

    def load_coords(self):
        file_path = filedialog.askopenfilename(filetypes=[('XYZ files', '*.xyz'), ('PDB files', '*.pdb'), ('All files', '*.*')])
        if not file_path:
            return
        with open(file_path, 'r') as f:
            self.coords_text.delete('1.0', tk.END)
            self.coords_text.insert(tk.END, f.read())
        self.update_preview_if_locked()

    def clear_coords(self):
        self.coords_text.delete('1.0', tk.END)
        self.update_preview_if_locked()

    def build_keywords(self):
        parts = [JOB_KEYWORDS.get(self.job_type.get(), '')]
        extras_vars = [
            (self.tightscf, 'TightSCF'), (self.d3bj, 'D3BJ'), (self.rij, 'RIJCOSX'),
            (self.grid5, 'Grid5'), (self.cpcm, 'CPCM'), (self.verytightscf, 'VeryTightSCF'),
            (self.slowconv, 'SlowConv'), (self.defgrid3, 'DefGrid3'), (self.defgridx, 'DefGridX')
        ]
        for var, label in extras_vars:
            if var.get():
                parts.append(label)
        if self.custom_keywords.get().strip():
            parts.append(self.custom_keywords.get().strip())
        return ' '.join([p for p in parts if p]).strip()

    def format_coords(self, text):
        text = text.strip()
        if not text:
            return ''
        lines = text.splitlines()
        if len(lines) > 1 and lines[0].strip().isdigit():
            coords = '\n'.join(lines[2:]).strip()
        else:
            coords = text
        return coords

    def build_input(self):
        header = '! ' + self.method.get().strip() + ' ' + self.basis.get().strip()
        extra_kw = self.build_keywords()
        if extra_kw:
            header += ' ' + extra_kw
        header += '\n\n'

        res_block = f"%maxcore {self.maxcore.get()}\n%pal nprocs {self.nprocs.get()} end\n\n"

        cpcm_block = ''
        if 'CPCM' in extra_kw or self.job_type.get() == 'Solvation' or self.cpcm.get():
            sol = self.solvent.get()
            cpcm_block = f'%cpcm\n  smd true\n  SMDsolvent "{sol}"\nend\n\n'

        coords = self.format_coords(self.coords_text.get('1.0', tk.END)) if self.auto_format_coords.get() else self.coords_text.get('1.0', tk.END).strip()
        xyz_block = ''
        if coords:
            xyz_block = f"* xyz {self.charge.get()} {self.mult.get()}\n{coords}\n*\n"

        custom_block_text = self.cb_text.get('1.0', tk.END).strip()
        if custom_block_text:
            custom_block_text += '\n\n'

        return header + res_block + cpcm_block + custom_block_text + xyz_block

    def update_preview(self):
        content = self.build_input()
        self.preview_text.delete('1.0', tk.END)
        self.preview_text.insert(tk.END, content)

    def update_preview_if_locked(self):
        if self.preview_locked.get():
            self.update_preview()

    def save_input(self):
        content = self.preview_text.get('1.0', tk.END) if not self.preview_locked.get() else self.build_input()
        if not content.strip():
            if not messagebox.askyesno('Empty Input', 'Preview is empty. Save anyway?'):
                return
        file_path = filedialog.asksaveasfilename(defaultextension='.inp', initialfile=self.out_name.get(), filetypes=[('ORCA input', '*.inp'), ('Text file', '*.txt'), ('All files', '*.*')])
        if file_path:
            with open(file_path, 'w') as f:
                f.write(content)
            messagebox.showinfo('Saved', f'Input saved to: {file_path}')

    def load_template(self):
        file_path = filedialog.askopenfilename(filetypes=[('ORCA input', '*.inp'), ('All files', '*.*')])
        if file_path:
            with open(file_path, 'r') as f:
                self.preview_text.delete('1.0', tk.END)
                self.preview_text.insert(tk.END, f.read())

    def save_template(self):
        file_path = filedialog.asksaveasfilename(defaultextension='.inp', filetypes=[('ORCA input', '*.inp'), ('All files', '*.*')])
        if file_path:
            with open(file_path, 'w') as f:
                f.write(self.preview_text.get('1.0', tk.END))

if __name__ == '__main__':
    app = ORCAInputBuilder()
    app.mainloop()