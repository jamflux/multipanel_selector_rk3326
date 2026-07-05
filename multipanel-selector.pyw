import os
import json
import shutil
import hashlib
import psutil
import tempfile
import re
import struct
import binascii
import mmap
import sys
import threading
import ctypes
from datetime import datetime
import customtkinter as ctk
from tkinter import filedialog
from pathlib import Path

# ================= MAGIA DND + PIL (ÍCONOS) =================
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    DND_SUPPORTED = True
    class CTkDnD(ctk.CTk, TkinterDnD.DnDWrapper):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.TkdndVersion = TkinterDnD._require(self)
except ImportError:
    DND_SUPPORTED = False
    class CTkDnD(ctk.CTk):
        pass

try:
    from PIL import Image, ImageDraw, ImageTk
except ImportError:
    pass

# ================= CONFIGURACIÓN VISUAL FLUX =================
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Paleta Refinada "Deep Cyber"
BG_FRAME = "#0B0C10"       
BTN_FLASH = "#8A2BE2"      # Violeta profundo (Acción crítica)
BTN_FLASH_HOV = "#9B30FF"  
BTN_ZIP = "#007FFF"        # Azul Azure
BTN_ZIP_HOV = "#005cbf"    
BTN_BACKUP = "#FF8C00"     # Naranja Oscuro
BTN_BACKUP_HOV = "#FF4500" # Naranja Rojizo (Hover)
BTN_INSPECT = "#008B8B"    # Cían oscuro
BTN_INSPECT_HOV = "#00FFFF" # Cían neón brillante

# ================= DICCIONARIOS DE IDIOMAS (i18n) =================
LANGUAGES = {
    "ES": {
        "title": "GoFluxDigital.com - Panel Detector & Flasher for RK3326 v1.0",
        "section_inject": "⚙️ DESPLIEGUE DE SISTEMA (MULTI-OS)",
        "waiting_sd": "Esperando unidad externa...",
        "sd_not_detected": "Volumen No Detectado",
        "os_target": "Entorno OS Objetivo:",
        "console_family": "Familia de Hardware:",
        "board_variant": "Variante de Placa:",
        "panel_model": "Modelo de Panel:",
        "btn_flash": "⚡ INYECTAR SISTEMA",
        "btn_zip": "📦 EXPORTAR A ZIP",
        "btn_backup": "💾 BACKUP DE SISTEMA",
        "section_inspect": "🔍 INSPECTOR FORENSE",
        "btn_inspect": "📂 Analizar Archivo DTB\n(o arrastra el archivo aquí)",
        "waiting_dtb": "[ A LA ESPERA DE ARCHIVO DTB ]",
        "db_error": "Anomalía en base de firmas criptográficas:\n{}",
        "empty": "Vacío",
        "not_found": "No Encontrado",
        "msg_sd_warning": "No se ha detectado ninguna unidad SD o volumen extraíble montado en el sistema.",
        "msg_base_dir_error": "Falta el directorio base del dispositivo:\n{}",
        "msg_success_inject": "El sistema {} ha sido inyectado y adaptado exitosamente.",
        "msg_admin_required": "Para realizar una lectura física del disco se requieren privilegios de Administrador.\n\nAl presionar ACEPTAR, la aplicación se reiniciará automáticamente solicitando los permisos necesarios.",
        "log_ready": "Sistema Flux Digital inicializado. A la espera de carga de archivos.",
        "log_db_loaded": "Firmas criptográficas cargadas en memoria: {}",
        "log_os_changed": "🔄 Entorno actualizado a: {}. Reconfigurando motor de inyección.",
        "log_invalid_file": "\n⚠️ Formato inválido. Por favor, asegúrate de utilizar un archivo tipo .dtb.",
        "log_analyzing": "=== EVALUANDO PAYLOAD: {} ===",
        "log_extracting": "\n🔍 EXTRACCIÓN DE PARÁMETROS (PRIORIDAD FDT/RAW):",
        "log_match_hex": "\n🎯 ¡COINCIDENCIA DE HARDWARE EXACTA (Vía Secuencia Hexadecimal)!",
        "log_identity_resolved": "  ➤ Identidad confirmada: {}",
        "log_integrity_ok": "  ➤ Integridad: 100% Original (Coincide con los registros locales)",
        "log_integrity_warn": "  ➤ Integridad: Archivo modificado o variante personalizada (Hash no coincide)",
        "log_match_forced": "\n🎯 ¡COINCIDENCIA MEDIANTE REGISTRO MAESTRO UNIVERSAL!",
        "log_identity_forced": "  ➤ Identidad forzada: {}",
        "log_hex_new": "\n⚠️ Secuencia Hexadecimal desconocida. El panel no está catalogado.",
        "log_no_seq": "\n⚠️ El archivo no contiene secuencias de inicialización de pantalla reconocibles.",
        "log_match_hash": "\n✅ COINCIDENCIA POR HASH (Archivo secundario):",
        "log_hash_fail": "❌ Hash desconocido. Imposible realizar validación forense.",
        "log_manual_req": "\n[!] Se requiere configuración manual del usuario.",
        "log_auto_adjust": "\n⚙️ AUTO-CONFIGURACIÓN APLICADA EXITOSAMENTE:",
        "log_missing_panel": "\n⚠️ Datos incompletos: El panel '{}' no existe en tu repositorio local.",
        "log_injecting": "=== INYECTANDO SISTEMA EN EL VOLUMEN [{}] ===",
        "log_inject_info": "Entorno: {} | Perfil de Hardware: {} > {} > {}\n",
        "log_transfer_dtb": "[1] Transfiriendo y adaptando Device Tree Blobs (DTBs)...",
        "log_patch_boot": "\n[2] Parcheando secuencias de configuración de arranque (Boot Config)...",
        "log_process_ok": "\n✅ Proceso FLUX completado de manera limpia y sin errores operativos.",
        "log_critical_fail": "\n[!] FALLO CRÍTICO DURANTE LA INYECCIÓN: {}",
        "log_pack_zip": "=== EMPAQUETANDO KIT DE DISTRIBUCIÓN PARA {} ===\n",
        "log_zip_ok": "\n✅ Kit de distribución exportado correctamente a: {}",
        "log_zip_fail": "\n[!] FALLO AL EMPAQUETAR: {}",
        "log_backup_start": "\n=== INICIANDO BACKUP DE SISTEMA ===",
        "log_backup_info": "  ➤ Origen Físico: {}\n  ➤ Tamaño estimado: {:.2f} GB",
        "log_backup_progress": "  ➤ Progreso: {}% completado...",
        "log_backup_progress_mb": "  ➤ Progreso: {:.2f} MB copiados...",
        "log_backup_ok": "\n✅ Backup completado exitosamente en:\n{}",
        "log_backup_err": "\n❌ Error al crear backup: {}",
        "log_backup_err_perm": "\n❌ Permisos insuficientes. Ejecute la aplicación como Administrador.",
        "msg_backup_ok": "El backup de imagen se ha guardado correctamente como:\n{}",
        "log_copy_rename": "  + Clonado y adaptado: {} -> {}",
        "log_copy_intact": "  + Clonado intacto: {}",
        "log_gen_uboot_dual": "  + Compilación U-Boot Dual: rg351v-uboot.dtb y rg351p-uboot.dtb",
        "log_gen_uboot_multi": "  + Compilación U-Boot Múltiple: rg351mp, rg351v y rg351p",
        "log_gen_kernel_dtb": "  + Compilación Kernel DTB: rg351mp-kernel.dtb y rg351p-kernel.dtb",
        "log_inject_kernel": "  + Se inyectó Kernel alternativo de manera segura (Image)",
        "log_no_kernel": "  ⚠️ Advertencia: No se encontró el Kernel alternativo en consolas/kernel/original/Image",
        "btn_error": "Error",
        "btn_success": "Éxito",
        "btn_warning": "Atención",
        "btn_ok": "ACEPTAR"
    },
    "EN": {
        "title": "GoFluxDigital.com - Panel Detector & Flasher for RK3326 v1.0",
        "section_inject": "⚙️ SYSTEM DEPLOYMENT (MULTI-OS)",
        "waiting_sd": "Waiting for external drive...",
        "sd_not_detected": "Volume Not Detected",
        "os_target": "Target OS Environment:",
        "console_family": "Hardware Family:",
        "board_variant": "Board Variant:",
        "panel_model": "Display Panel Model:",
        "btn_flash": "⚡ INJECT SYSTEM",
        "btn_zip": "📦 PACKAGE DISTRIBUTION KIT",
        "btn_backup": "💾 SYSTEM BACKUP",
        "section_inspect": "🔍 FORENSIC INSPECTOR",
        "btn_inspect": "📂 Analyze DTB File\n(or drag & drop file here)",
        "waiting_dtb": "[ AWAITING DTB FILE ]",
        "db_error": "Cryptographic signature database is corrupted or inaccessible:\n{}",
        "empty": "Empty",
        "not_found": "Not Found",
        "msg_sd_warning": "No valid SD volume or removable drive has been detected in the system.",
        "msg_base_dir_error": "Missing base device directory:\n{}",
        "msg_success_inject": "The {} environment has been successfully injected and adapted.",
        "msg_admin_required": "To perform a physical disk read, Administrator privileges are required.\n\nBy clicking OK, the application will automatically restart and request the necessary permissions.",
        "log_ready": "Flux Digital System initialized. Awaiting payload.",
        "log_db_loaded": "Cryptographic signatures loaded into memory: {}",
        "log_os_changed": "🔄 Environment updated to: {}. Reconfiguring injection engine.",
        "log_invalid_file": "\n⚠️ Invalid format. Please make sure to drop a valid .dtb file.",
        "log_analyzing": "=== EVALUATING PAYLOAD: {} ===",
        "log_extracting": "\n🔍 HARDWARE PARAMETER EXTRACTION (FDT/RAW PRIORITY):",
        "log_match_hex": "\n🎯 EXACT HARDWARE MATCH! (Via Hex Sequence)",
        "log_identity_resolved": "  ➤ Identity confirmed as: {}",
        "log_integrity_ok": "  ➤ Integrity: 100% Original (Matches local records)",
        "log_integrity_warn": "  ➤ Integrity: Modified file or custom variant (Hash mismatch)",
        "log_match_forced": "\n🎯 MATCH VIA UNIVERSAL MASTER RECORD!",
        "log_identity_forced": "  ➤ Forced identity: {}",
        "log_hex_new": "\n⚠️ Unknown Hex Sequence. The display panel is uncataloged.",
        "log_no_seq": "\n⚠️ The file lacks recognizable display initialization sequences.",
        "log_match_hash": "\n✅ HASH MATCH (Secondary file):",
        "log_hash_fail": "❌ Unknown Hash. Forensic validation is impossible.",
        "log_manual_req": "\n[!] Manual user configuration is required.",
        "log_auto_adjust": "\n⚙️ AUTO-CONFIGURATION SUCCESSFULLY APPLIED:",
        "log_missing_panel": "\n⚠️ Incomplete data: The panel '{}' does not exist in your local repository.",
        "log_injecting": "=== INJECTING SYSTEM INTO VOLUME [{}] ===",
        "log_inject_info": "Environment: {} | Hardware Profile: {} > {} > {}\n",
        "log_transfer_dtb": "[1] Transferring and adapting Device Tree Blobs (DTBs)...",
        "log_patch_boot": "\n[2] Patching boot configuration sequences (Boot Config)...",
        "log_process_ok": "\n✅ FLUX Deployment completed cleanly with no operational errors.",
        "log_critical_fail": "\n[!] CRITICAL FAILURE DURING INJECTION: {}",
        "log_pack_zip": "=== PACKAGING DISTRIBUTION KIT FOR {} ===\n",
        "log_zip_ok": "\n✅ Distribution Kit successfully exported to: {}",
        "log_zip_fail": "\n[!] PACKAGING FAILURE: {}",
        "log_backup_start": "\n=== STARTING SYSTEM BACKUP ===",
        "log_backup_info": "  ➤ Physical Source: {}\n  ➤ Estimated size: {:.2f} GB",
        "log_backup_progress": "  ➤ Progress: {}% completed...",
        "log_backup_progress_mb": "  ➤ Progress: {:.2f} MB copied...",
        "log_backup_ok": "\n✅ Backup successfully completed at:\n{}",
        "log_backup_err": "\n❌ Backup error: {}",
        "log_backup_err_perm": "\n❌ Insufficient permissions. Run the application as Administrator.",
        "msg_backup_ok": "The image backup was successfully saved as:\n{}",
        "log_copy_rename": "  + Cloned and adapted: {} -> {}",
        "log_copy_intact": "  + Cloned intact: {}",
        "log_gen_uboot_dual": "  + Dual U-Boot Compilation: rg351v-uboot.dtb & rg351p-uboot.dtb",
        "log_gen_uboot_multi": "  + Multi U-Boot Compilation: rg351mp, rg351v & rg351p",
        "log_gen_kernel_dtb": "  + Kernel DTB Compilation: rg351mp-kernel.dtb & rg351p-kernel.dtb",
        "log_inject_kernel": "  + Alternative Kernel safely injected (Image)",
        "log_no_kernel": "  ⚠️ Warning: Alternative Kernel not found in consolas/kernel/original/Image",
        "btn_error": "Error",
        "btn_success": "Success",
        "btn_warning": "Notice",
        "btn_ok": "OK"
    }
}

# ================= CLASE FLUX DIALOG (INTERFAZ MODERNA) =================
class FluxDialog(ctk.CTkToplevel):
    def __init__(self, master, title, message, dialog_type="info"):
        super().__init__(master)
        
        self.title(title)
        self.geometry("480x260")
        self.resizable(False, False)
        self.configure(fg_color=BG_FRAME)
        self.attributes("-topmost", True)
        self.transient(master)
        
        self.result = False
        
        # Mapa de colores según el contexto
        if dialog_type == "error":
            color = "#FF4C4C"
        elif dialog_type == "warning":
            color = "#FFD700"
        elif dialog_type == "success":
            color = "#00FFFF" 
        else:
            color = BTN_INSPECT
            
        self.update_idletasks()
        # Centrar sobre la ventana maestra
        x = master.winfo_x() + (master.winfo_width() // 2) - (480 // 2)
        y = master.winfo_y() + (master.winfo_height() // 2) - (260 // 2)
        self.geometry(f"+{x}+{y}")
        
        self.lbl_title = ctk.CTkLabel(self, text=title.upper(), font=ctk.CTkFont(weight="bold", size=16), text_color=color)
        self.lbl_title.pack(pady=(20, 5))
        
        self.lbl_message = ctk.CTkLabel(self, text=message, font=ctk.CTkFont(size=13), text_color="#FFFFFF", wraplength=420, justify="center")
        self.lbl_message.pack(pady=(0, 15), padx=20, expand=True)
        
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=(0, 20))
        
        # El idioma se transfiere desde el master
        txt_ok = master.t("btn_ok") if hasattr(master, 't') else "OK"
        
        self.btn_ok = ctk.CTkButton(self.btn_frame, text=txt_ok, width=130, height=35, fg_color=color, hover_color=color, text_color="#000000", font=ctk.CTkFont(weight="bold"), command=self.on_yes)
        self.btn_ok.pack()
        
        self.after(200, self._apply_icon)
        self.grab_set()
        master.wait_window(self)
        
    def _apply_icon(self):
        try:
            icon_path = os.path.join(tempfile.gettempdir(), "flux_cyber_icon.ico")
            if os.path.exists(icon_path) and os.name == 'nt':
                self.wm_iconbitmap(icon_path)
                self.iconbitmap(icon_path)
        except Exception:
            pass

    def on_yes(self):
        self.result = True
        self.destroy()

class FluxMasterFlasher(CTkDnD):
    FDT_MAGIC = 0xd00dfeed
    FDT_BEGIN_NODE = 0x1
    FDT_END_NODE = 0x2
    FDT_PROP = 0x3
    FDT_NOP = 0x4
    FDT_END = 0x9

    def __init__(self):
        super().__init__()
        
        self.current_lang = "ES"
        self._bypass_uipi()
        
        self.title(self.t("title"))
        self.geometry("980x590")
        self.minsize(880, 570)
        self.configure(fg_color=BG_FRAME)
        
        self.apply_dynamic_icon()
        
        self.db_path = Path("consolas/database.json")
        self.base_consolas = Path("consolas")
        
        self.db_firmas = {}
        self.target_drive = ctk.StringVar(value=self.t("waiting_sd"))
        self.is_backing_up = False
        
        self.cargar_base_datos()
        self.construir_ui()
        self.auto_detect_sd()

    def _bypass_uipi(self):
        """Intenta evadir el bloqueo UIPI de Windows cuando se ejecuta como Administrador para permitir Drag&Drop"""
        if os.name == 'nt':
            try:
                MSGFLT_ADD = 1
                WM_DROPFILES = 0x0233
                WM_COPYDATA = 0x004A
                WM_COPYGLOBALDATA = 0x0049
                
                ctypes.windll.user32.ChangeWindowMessageFilter(WM_DROPFILES, MSGFLT_ADD)
                ctypes.windll.user32.ChangeWindowMessageFilter(WM_COPYDATA, MSGFLT_ADD)
                ctypes.windll.user32.ChangeWindowMessageFilter(WM_COPYGLOBALDATA, MSGFLT_ADD)
            except Exception:
                pass

    def apply_dynamic_icon(self):
        try:
            if 'PIL' not in sys.modules: return
            icon_path = os.path.join(tempfile.gettempdir(), "flux_cyber_icon.ico")
            
            if not os.path.exists(icon_path):
                img = Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
                draw = ImageDraw.Draw(img)
                
                # Diseño tipo Microchip/CPU acorde a la paleta Dark Cyber
                draw.rounded_rectangle([8, 8, 56, 56], radius=6, fill="#121417", outline="#00FFFF", width=3)
                draw.rectangle([22, 22, 42, 42], fill="#8A2BE2", outline="#00FFFF", width=2)
                draw.line([32, 8, 32, 22], fill="#00FFFF", width=3)
                draw.line([8, 32, 22, 32], fill="#00FFFF", width=3)
                draw.line([42, 32, 56, 32], fill="#00FFFF", width=3)
                draw.line([32, 42, 32, 56], fill="#00FFFF", width=3)
                
                img.save(icon_path, format="ICO", sizes=[(64, 64)])
            
            if os.name == 'nt' and os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception:
            pass

    def t(self, key):
        return LANGUAGES[self.current_lang].get(key, key)

    def toggle_language(self, choice):
        self.current_lang = choice
        self.update_ui_texts()
        
        # Limpiar la consola y reescribir los logs iniciales en el idioma correcto
        self.consola.configure(state="normal")
        self.consola.delete("0.0", "end")
        self.consola.configure(state="disabled")
        
        self.registrar_log(self.t("log_ready"), "success")
        self.registrar_log(self.t("log_db_loaded").format(len(self.db_firmas)), "info")
        
    def cargar_base_datos(self):
        if self.db_path.exists():
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    raw_db = json.load(f)
                if isinstance(raw_db, list):
                    self.db_firmas = {item.get("sha256"): item for item in raw_db if "sha256" in item}
                else:
                    self.db_firmas = raw_db
            except Exception as e:
                FluxDialog(self, self.t("btn_error"), self.t("db_error").format(e), "error")
                
    def construir_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ================= PANEL IZQUIERDO =================
        self.left_panel = ctk.CTkFrame(self, width=310, corner_radius=8, fg_color="#121417")
        self.left_panel.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")
        
        # Selector de Idioma (i18n)
        self.seg_lang = ctk.CTkSegmentedButton(
            self.left_panel, 
            values=["ES", "EN"], 
            command=self.toggle_language, 
            selected_color=BTN_INSPECT, 
            selected_hover_color=BTN_INSPECT_HOV,
            unselected_color="#7A7A7A",        
            unselected_hover_color="#8A8A8A",  
            fg_color="#4A4D55",                
            text_color="#000000"               
        )
        self.seg_lang.set("ES")
        self.seg_lang.pack(fill="x", padx=15, pady=(10, 5))

        self.lbl_inject_title = ctk.CTkLabel(self.left_panel, text=self.t("section_inject"), font=ctk.CTkFont(size=14, weight="bold"), text_color="#FFFFFF")
        self.lbl_inject_title.pack(pady=(10, 5))
        
        self.lbl_drive = ctk.CTkLabel(self.left_panel, textvariable=self.target_drive, text_color="#00FFFF", font=ctk.CTkFont(weight="bold", size=12))
        self.lbl_drive.pack(anchor="w", padx=15, pady=(0, 10))
        
        self.lbl_os = ctk.CTkLabel(self.left_panel, text=self.t("os_target"), text_color="#A0A0A0")
        self.lbl_os.pack(anchor="w", padx=15)
        self.cb_os = ctk.CTkComboBox(self.left_panel, values=["ArkOS 4 Clone", "ArkOS Original", "dArkOS", "dArkOS RE"], height=30, command=self.on_os_change)
        self.cb_os.pack(fill="x", padx=15, pady=(0, 15))
        
        self.lbl_console = ctk.CTkLabel(self.left_panel, text=self.t("console_family"), text_color="#A0A0A0")
        self.lbl_console.pack(anchor="w", padx=15)
        self.cb_consola = ctk.CTkComboBox(self.left_panel, command=self.actualizar_variantes, height=30)
        self.cb_consola.pack(fill="x", padx=15, pady=(0, 15))

        self.lbl_variant = ctk.CTkLabel(self.left_panel, text=self.t("board_variant"), text_color="#A0A0A0")
        self.lbl_variant.pack(anchor="w", padx=15)
        self.cb_variante = ctk.CTkComboBox(self.left_panel, command=self.actualizar_paneles, height=30)
        self.cb_variante.pack(fill="x", padx=15, pady=(0, 15))
        
        self.lbl_panel = ctk.CTkLabel(self.left_panel, text=self.t("panel_model"), text_color="#A0A0A0")
        self.lbl_panel.pack(anchor="w", padx=15)
        self.cb_panel = ctk.CTkComboBox(self.left_panel, height=30)
        self.cb_panel.pack(fill="x", padx=15, pady=(0, 20))
        
        self.btn_flash = ctk.CTkButton(self.left_panel, text=self.t("btn_flash"), height=40, text_color="#FFFFFF", fg_color=BTN_FLASH, hover_color=BTN_FLASH_HOV, font=ctk.CTkFont(weight="bold", size=13), command=self.flashear_archivos)
        self.btn_flash.pack(fill="x", padx=15, pady=(10, 5))
        
        self.btn_zip = ctk.CTkButton(self.left_panel, text=self.t("btn_zip"), height=35, text_color="#000000", fg_color=BTN_ZIP, hover_color=BTN_ZIP_HOV, font=ctk.CTkFont(weight="bold", size=12), command=self.exportar_zip)
        self.btn_zip.pack(fill="x", padx=15, pady=(5, 5))

        self.btn_backup = ctk.CTkButton(self.left_panel, text=self.t("btn_backup"), height=35, text_color="#000000", fg_color=BTN_BACKUP, hover_color=BTN_BACKUP_HOV, font=ctk.CTkFont(weight="bold", size=12), command=self.ejecutar_backup)
        self.btn_backup.pack(fill="x", padx=15, pady=(5, 10))

        # ================= PANEL DERECHO (INSPECTOR) =================
        self.right_panel = ctk.CTkFrame(self, corner_radius=8, fg_color="#121417")
        self.right_panel.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="nsew")
        
        self.lbl_inspect_title = ctk.CTkLabel(self.right_panel, text=self.t("section_inspect"), font=ctk.CTkFont(size=15, weight="bold"), text_color="#FFFFFF")
        self.lbl_inspect_title.pack(pady=(15, 5))
        
        self.btn_inspect = ctk.CTkButton(
            self.right_panel, 
            text=self.t("btn_inspect"), 
            height=50, 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#000000",
            fg_color=BTN_INSPECT, 
            hover_color=BTN_INSPECT_HOV, 
            command=self.inspeccionar_archivo_dialog
        )
        self.btn_inspect.pack(pady=(5, 5), padx=20, fill="x")

        # --- COMPONENTE GIGANTE DE IDENTIFICACIÓN ---
        self.lbl_pantalla_detectada = ctk.CTkLabel(
            self.right_panel, 
            text=self.t("waiting_dtb"), 
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#555555"
        )
        self.lbl_pantalla_detectada.pack(pady=(5, 10))
        
        # Consola Log
        self.consola = ctk.CTkTextbox(self.right_panel, font=ctk.CTkFont(family="Consolas", size=13), fg_color="#000000", border_color="#1A1C23", border_width=1)
        self.consola.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        self.consola.tag_config("info", foreground="#A0A0A0")
        self.consola.tag_config("success", foreground="#00FFFF") 
        self.consola.tag_config("warning", foreground="#FFD700") 
        self.consola.tag_config("error", foreground="#FF4C4C")
        self.consola.tag_config("hex", foreground="#00FFFF")
        self.consola.tag_config("gpio", foreground="#FFD700")
        self.consola.tag_config("title", foreground="#FFFFFF")

        self.cargar_consolas_locales()
        self.registrar_log(self.t("log_ready"), "success")
        self.registrar_log(self.t("log_db_loaded").format(len(self.db_firmas)), "info")

        if DND_SUPPORTED:
            self.btn_inspect.drop_target_register(DND_FILES)
            self.btn_inspect.dnd_bind('<<Drop>>', self.on_drop_dtb)
            self.consola.drop_target_register(DND_FILES)
            self.consola.dnd_bind('<<Drop>>', self.on_drop_dtb)
            self.lbl_pantalla_detectada.drop_target_register(DND_FILES)
            self.lbl_pantalla_detectada.dnd_bind('<<Drop>>', self.on_drop_dtb)
            self.right_panel.drop_target_register(DND_FILES)
            self.right_panel.dnd_bind('<<Drop>>', self.on_drop_dtb)

    def update_ui_texts(self):
        self.title(self.t("title"))
        self.lbl_inject_title.configure(text=self.t("section_inject"))
        self.lbl_os.configure(text=self.t("os_target"))
        self.lbl_console.configure(text=self.t("console_family"))
        self.lbl_variant.configure(text=self.t("board_variant"))
        self.lbl_panel.configure(text=self.t("panel_model"))
        self.btn_flash.configure(text=self.t("btn_flash"))
        self.btn_zip.configure(text=self.t("btn_zip"))
        self.btn_backup.configure(text=self.t("btn_backup"))
        self.lbl_inspect_title.configure(text=self.t("section_inspect"))
        self.btn_inspect.configure(text=self.t("btn_inspect"))
        
        current_sd = self.target_drive.get()
        if current_sd in [LANGUAGES["ES"]["waiting_sd"], LANGUAGES["EN"]["waiting_sd"]]:
            self.target_drive.set(self.t("waiting_sd"))
        elif current_sd in [LANGUAGES["ES"]["sd_not_detected"], LANGUAGES["EN"]["sd_not_detected"]]:
            self.target_drive.set(self.t("sd_not_detected"))
            
        current_dtb = self.lbl_pantalla_detectada.cget("text")
        if current_dtb in [LANGUAGES["ES"]["waiting_dtb"], LANGUAGES["EN"]["waiting_dtb"]]:
            self.lbl_pantalla_detectada.configure(text=self.t("waiting_dtb"))

    def registrar_log(self, texto, tag="info"):
        self.consola.configure(state="normal")
        self.consola.insert("end", texto + "\n", tag)
        self.consola.see("end")
        self.consola.configure(state="disabled")

    def limpiar_log(self):
        self.consola.configure(state="normal")
        self.consola.delete("0.0", "end")
        self.consola.configure(state="disabled")
        self.lbl_pantalla_detectada.configure(text=self.t("waiting_dtb"), text_color="#555555")

    def on_os_change(self, choice):
        self.registrar_log(self.t("log_os_changed").format(choice), "warning")

    # ================= FILTRO SEMÁNTICO (UX) =================
    def limpiar_texto_ux(self, variante, panel):
        var_limpia = variante.replace('_', ' ')
        pan_limpio = panel.replace('_', ' ')
        
        palabras_variante = set(var_limpia.lower().split())
        palabras_panel = pan_limpio.split()
        
        panel_filtrado = []
        for p in palabras_panel:
            if p.lower() not in palabras_variante:
                panel_filtrado.append(p)
                
        pan_limpio = " ".join(panel_filtrado)
        
        pan_limpio = re.sub(r'([a-zA-Z])(\d+)', r'\1 \2', pan_limpio)
        var_limpia = re.sub(r'([a-zA-Z])(\d+)', r'\1 \2', var_limpia)
        
        pan_limpio = pan_limpio.title().strip() or "Default"
        var_limpia = var_limpia.title().strip()
        
        return var_limpia, pan_limpio

    # ================= FUNCIONES UI CASCADA =================
    def cargar_consolas_locales(self):
        if not self.base_consolas.exists():
            self.cb_consola.configure(values=[self.t("not_found")])
            return
        consolas = [d.name for d in self.base_consolas.iterdir() if d.is_dir()]
        if consolas:
            self.cb_consola.configure(values=consolas)
            self.cb_consola.set(consolas[0])
            self.actualizar_variantes(consolas[0])

    def actualizar_variantes(self, consola_seleccionada):
        ruta_consola = self.base_consolas / consola_seleccionada
        if ruta_consola.exists():
            variantes = [d.name for d in ruta_consola.iterdir() if d.is_dir()]
            if variantes:
                self._mapa_variantes = {self.limpiar_texto_ux(v, "dummy")[0]: v for v in variantes}
                nombres_limpios = list(self._mapa_variantes.keys())
                
                self.cb_variante.configure(values=nombres_limpios)
                self.cb_variante.set(nombres_limpios[0])
                self.actualizar_paneles(nombres_limpios[0])
            else:
                self.vaciar_combobox(self.cb_variante)
                self.vaciar_combobox(self.cb_panel)

    def actualizar_paneles(self, variante_ux_seleccionada):
        consola = self.cb_consola.get()
        variante_real = self._mapa_variantes.get(variante_ux_seleccionada, variante_ux_seleccionada)
        ruta_variante = self.base_consolas / consola / variante_real
        
        if ruta_variante.exists():
            paneles = [d.name for d in ruta_variante.iterdir() if d.is_dir()]
            if paneles:
                self._mapa_paneles = {self.limpiar_texto_ux(variante_real, p)[1]: p for p in paneles}
                paneles_limpios = list(self._mapa_paneles.keys())
                
                self.cb_panel.configure(values=paneles_limpios)
                self.cb_panel.set(paneles_limpios[0])
            else:
                self.vaciar_combobox(self.cb_panel)

    def vaciar_combobox(self, widget):
        widget.configure(values=[self.t("empty")])
        widget.set(self.t("empty"))

    def auto_detect_sd(self):
        for p in psutil.disk_partitions():
            if 'removable' in p.opts or 'cdrom' not in p.opts:
                mnt = Path(p.mountpoint)
                if (mnt / "boot.ini").exists() or (mnt / "uInitrd").exists() or (mnt / "Image").exists():
                    self.target_drive.set(p.mountpoint)
                    return
        self.target_drive.set(self.t("sd_not_detected"))
        self.after(3000, self.auto_detect_sd)

    # ================= SISTEMA DE BACKUP =================
    def get_physical_drive(self, mountpoint):
        if os.name == 'nt':
            try:
                import wmi
                import pythoncom
                pythoncom.CoInitialize()
                c = wmi.WMI()
                drive_letter = os.path.splitdrive(mountpoint)[0]
                
                # LogicalDisk -> Partition -> DiskDrive 
                for part in c.query(f"ASSOCIATORS OF {{Win32_LogicalDisk.DeviceID='{drive_letter}'}} WHERE AssocClass=Win32_LogicalDiskToPartition"):
                    for disk in c.query(f"ASSOCIATORS OF {{Win32_DiskPartition.DeviceID='{part.DeviceID}'}} WHERE AssocClass=Win32_DiskDriveToDiskPartition"):
                        dev_id = disk.DeviceID
                        size = int(disk.Size) if disk.Size else 0
                        pythoncom.CoUninitialize()
                        return dev_id, size
                pythoncom.CoUninitialize()
            except Exception:
                pass
            
            # Fallback en caso de que WMI falle o no encuentre
            drive_letter = os.path.splitdrive(mountpoint)[0]
            try:
                size = shutil.disk_usage(mountpoint).total
            except:
                size = 0
            return f"\\\\.\\{drive_letter}", size
        else:
            for p in psutil.disk_partitions():
                if p.mountpoint == mountpoint:
                    dev = p.device
                    base_dev = re.sub(r'\d+$', '', dev)
                    return base_dev, 0
            return None, 0

    def ejecutar_backup(self):
        sd_path = self.target_drive.get()
        if not os.path.exists(sd_path) or "Esperando" in sd_path or "Waiting" in sd_path or "No Detectada" in sd_path or "Not Detected" in sd_path:
            FluxDialog(self, self.t("btn_warning"), self.t("msg_sd_warning"), "warning")
            return

        # Verificación de privilegios de administrador en Windows
        if os.name == 'nt':
            try:
                is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            except Exception:
                is_admin = False
                
            if not is_admin:
                dialog = FluxDialog(self, self.t("btn_warning"), self.t("msg_admin_required"), "warning")
                if dialog.result:
                    script_path = os.path.abspath(sys.argv[0])
                    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script_path}"', None, 1)
                    sys.exit()
                return

        if self.is_backing_up:
            return
            
        self.is_backing_up = True
        threading.Thread(target=self._backup_worker, args=(sd_path,), daemon=True).start()

    def _backup_worker(self, sd_path):
        self.registrar_log(self.t("log_backup_start"), "title")
        
        try:
            raw_device, total_size = self.get_physical_drive(sd_path)
            if not raw_device:
                raise Exception("No se detectó el dispositivo físico.")
            
            backup_dir = Path("backup")
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%d%m%Y%H%M")
            backup_filename = f"{timestamp}.img"
            backup_path = backup_dir / backup_filename
            
            if total_size > 0:
                self.registrar_log(self.t("log_backup_info").format(raw_device, total_size / (1024**3)), "info")
            else:
                self.registrar_log(self.t("log_backup_info").format(raw_device, 0.0), "info")
                
            chunk_size = 16 * 1024 * 1024 # 16 MB chunks
            sector_size = 512
            bytes_read = 0
            last_percent = -1
            last_mb = 0
            
            with open(raw_device, "rb") as src, open(backup_path, "wb") as dst:
                while True:
                    if total_size > 0 and bytes_read >= total_size:
                        break # Fin exitoso (Leímos todo el disco)
                        
                    bytes_to_read = chunk_size
                    if total_size > 0 and (total_size - bytes_read) < chunk_size:
                        bytes_to_read = int(total_size - bytes_read)
                        rem = bytes_to_read % sector_size
                        if rem != 0: 
                            bytes_to_read += (sector_size - rem) # Alinear estricto a sector
                            
                    try:
                        chunk = src.read(bytes_to_read)
                    except OSError as e:
                        # Si el Kernel bloquea el I/O al chocar con el límite final del disco lo tratamos como EOF
                        if bytes_read > 0 and (total_size == 0 or (total_size - bytes_read) < (chunk_size * 2)):
                            break
                        raise e
                        
                    if not chunk:
                        break
                        
                    # Truncamos los bytes de relleno para guardar el tamaño exacto si nos pasamos por el alineamiento de sector
                    actual_len = len(chunk)
                    if total_size > 0 and bytes_read + actual_len > total_size:
                        actual_len = int(total_size - bytes_read)
                        chunk = chunk[:actual_len]
                        
                    dst.write(chunk)
                    bytes_read += actual_len
                    
                    if total_size > 0:
                        percent = int((bytes_read / total_size) * 100)
                        if percent % 5 == 0 and percent != last_percent:
                            self.registrar_log(self.t("log_backup_progress").format(percent), "info")
                            last_percent = percent
                    else:
                        mb_read = bytes_read / (1024**2)
                        if mb_read - last_mb >= 500: # Log cada 500 MB si no se conoce el límite
                            self.registrar_log(self.t("log_backup_progress_mb").format(mb_read), "info")
                            last_mb = mb_read
                            
            self.registrar_log(self.t("log_backup_ok").format(backup_path.resolve()), "success")
            self.after(0, lambda: FluxDialog(self, self.t("btn_success"), self.t("msg_backup_ok").format(backup_filename), "success"))
            
        except PermissionError:
            self.registrar_log(self.t("log_backup_err_perm"), "error")
            self.after(0, lambda: FluxDialog(self, self.t("btn_error"), self.t("log_backup_err_perm"), "error"))
        except Exception as e:
            self.registrar_log(self.t("log_backup_err").format(e), "error")
            self.after(0, lambda: FluxDialog(self, self.t("btn_error"), self.t("log_backup_err").format(e), "error"))
        finally:
            self.is_backing_up = False

    # ================= MOTOR FDT NATIVO =================
    @staticmethod
    def _align(offset, alignment=4):
        return (offset + (alignment - 1)) & ~(alignment - 1)

    def parsear_fdt_dinamico(self, filepath):
        target_properties = {b'panel-init-sequence', b'compatible', b'reset-gpios', b'enable-gpios'}
        extracted = {}
        try:
            with open(filepath, "rb") as f:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as data:
                    header_format = ">10I"
                    header_size = struct.calcsize(header_format)
                    if len(data) < header_size: return extracted

                    magic, _, off_dt_struct, off_dt_strings, _, _, _, _, size_dt_strings, size_dt_struct = struct.unpack(header_format, data[:header_size])
                    if magic != self.FDT_MAGIC: return extracted

                    struct_block = data[off_dt_struct : off_dt_struct + size_dt_struct]
                    strings_block = data[off_dt_strings : off_dt_strings + size_dt_strings]

                    p = 0
                    while p < len(struct_block):
                        tag = struct.unpack(">I", struct_block[p:p+4])[0]
                        p += 4

                        if tag == self.FDT_BEGIN_NODE:
                            null_idx = struct_block.find(b'\x00', p)
                            if null_idx == -1: break
                            p = self._align(null_idx + 1)
                        elif tag == self.FDT_END_NODE or tag == self.FDT_NOP:
                            continue
                        elif tag == self.FDT_PROP:
                            length, nameoff = struct.unpack(">2I", struct_block[p:p+8])
                            p += 8
                            prop_data = struct_block[p:p+length]
                            p = self._align(p + length)

                            name_end = strings_block.find(b'\x00', nameoff)
                            if name_end == -1: continue
                            prop_name = strings_block[nameoff:name_end]

                            if prop_name in target_properties:
                                key = prop_name.decode('utf-8')
                                if prop_name == b'panel-init-sequence':
                                    extracted[key] = binascii.hexlify(prop_data).decode('utf-8')
                                elif prop_name in (b'reset-gpios', b'enable-gpios'):
                                    cells = length // 4
                                    if cells > 0:
                                        extracted[key] = struct.unpack(f">{cells}I", prop_data)
                        elif tag == self.FDT_END:
                            break
        except Exception as e:
            self.registrar_log(f"FDT Error: {e}", "error")
        return extracted

    # ================= INSPECCIÓN FDT FIRST Y RAW BINARY =================
    def deducir_clasificacion(self, nombre_archivo):
        partes = nombre_archivo.lower().replace(".dtb", "").split('-')
        if len(partes) < 3 or partes[0] != "rk3326" or partes[-1] != "linux": return None, None, None
            
        consola = partes[1].upper()
        elementos_medio = partes[2:-1]
        variante, panel = "Original", "Default"
        
        if elementos_medio:
            cadena_medio = "-".join(elementos_medio)
            if consola == 'R36S':
                if 'sauce' in cadena_medio: variante = 'Soy_Sauce'
                elif 'type' in cadena_medio or 'clone' in cadena_medio: variante = 'Clone'
                else: variante = 'Original'
            panel = "_".join(p.capitalize() for p in elementos_medio)
            
        return consola, variante, panel

    def inspeccionar_archivo_dialog(self):
        filepath = filedialog.askopenfilename(title="DTB Payload", filetypes=[("Device Tree", "*.dtb")])
        if filepath:
            self.procesar_inspeccion(filepath)

    def on_drop_dtb(self, event):
        filepath = event.data.strip("{}") if hasattr(event, 'data') else ""
        if not filepath.lower().endswith(".dtb"):
            self.registrar_log(self.t("log_invalid_file"), "error")
            return
        self.procesar_inspeccion(filepath)

    def procesar_inspeccion(self, filepath):
        self.limpiar_log()
        self.registrar_log(self.t("log_analyzing").format(Path(filepath).name), "title")
        
        with open(filepath, "rb") as f:
            binario = f.read()
            
        file_hash = hashlib.sha256(binario).hexdigest()
        identificador_archivo = Path(filepath).name
        match_exitoso = False

        maestro_pantallas = {
            "0596011105320129": "rk3326-r36s-sauce-panel2-linux.dtb",
            "390004efffff0105c8011105320129": "rk3326-r36s-linux.dtb",
            "05c8011115000236c0050a0129": "rk3326-a10mini-linux.dtb",
        }

        props_extraidas = self.parsear_fdt_dinamico(filepath)
        secuencia_hex_local = props_extraidas.get("panel-init-sequence")
        
        if not secuencia_hex_local:
            for seq_hex in maestro_pantallas.keys():
                if bytes.fromhex(seq_hex) in binario:
                    secuencia_hex_local = seq_hex
                    props_extraidas['panel-init-sequence (Incrustada)'] = seq_hex
                    break
            if not secuencia_hex_local:
                for data in self.db_firmas.values():
                    db_seq = data.get("properties", {}).get("panel-init-sequence")
                    if db_seq and bytes.fromhex(db_seq) in binario:
                        secuencia_hex_local = db_seq
                        props_extraidas['panel-init-sequence (Raw DB)'] = db_seq
                        break
                        
        self.registrar_log(self.t("log_extracting"), "title")
        self._imprimir_propiedades(props_extraidas)

        if secuencia_hex_local:
            posibles_matches = []
            for db_hash, data in self.db_firmas.items():
                db_props = data.get("properties", {})
                if db_props.get("panel-init-sequence") == secuencia_hex_local:
                    posibles_matches.append((db_hash, data))
            
            if posibles_matches:
                posibles_matches.sort(key=lambda x: 0 if "linux.dtb" in x[1].get("file", "").lower() else 1)
                best_match_hash, best_match_data = posibles_matches[0]
                identificador_archivo = best_match_data.get("file", identificador_archivo)
                match_exitoso = True
                
                self.registrar_log(self.t("log_match_hex"), "success")
                self.registrar_log(self.t("log_identity_resolved").format(identificador_archivo), "info")
                
                if best_match_hash == file_hash:
                    self.registrar_log(self.t("log_integrity_ok"), "success")
                else:
                    self.registrar_log(self.t("log_integrity_warn"), "warning")

            elif secuencia_hex_local in maestro_pantallas:
                identificador_archivo = maestro_pantallas[secuencia_hex_local]
                self.registrar_log(self.t("log_match_forced"), "success")
                self.registrar_log(self.t("log_identity_forced").format(identificador_archivo), "info")
                match_exitoso = True
                
            if not match_exitoso:
                self.registrar_log(self.t("log_hex_new"), "error")
        else:
            self.registrar_log(self.t("log_no_seq"), "warning")
            if file_hash in self.db_firmas:
                data = self.db_firmas[file_hash]
                identificador_archivo = data.get("file", identificador_archivo)
                self.registrar_log(self.t("log_match_hash"), "success")
                self.registrar_log(self.t("log_identity_resolved").format(identificador_archivo), "info")
                match_exitoso = True
            else:
                self.registrar_log(self.t("log_hash_fail"), "error")

        if match_exitoso:
            self.ejecutar_auto_ajuste(identificador_archivo)
        else:
            self.lbl_pantalla_detectada.configure(text="⚠️ HARDWARE DESCONOCIDO", text_color="#FF4C4C")
            self.registrar_log(self.t("log_manual_req"), "warning")

    def _imprimir_propiedades(self, props):
        for k, v in props.items():
            if 'panel-init-sequence' in k:
                val_str = str(v)[:60] + "..." if len(str(v)) > 60 else str(v)
                self.registrar_log(f"      🔹 {k.upper()}: {val_str}", "hex")
            elif 'gpios' in k:
                self.registrar_log(f"      🔹 {k.upper()}: {v}", "gpio")
            else:
                self.registrar_log(f"      🔹 {k.upper()}: {v}", "info")

    def ejecutar_auto_ajuste(self, nombre_archivo):
        consola, variante, panel = self.deducir_clasificacion(nombre_archivo)
        if not consola: return
            
        valores_consola = self.cb_consola.cget("values")
        if valores_consola and consola in valores_consola:
            self.cb_consola.set(consola)
            self.actualizar_variantes(consola)
            
            var_ux, pan_ux = self.limpiar_texto_ux(variante, panel)
            valores_variante_ux = self.cb_variante.cget("values")
            
            if valores_variante_ux and var_ux in valores_variante_ux:
                self.cb_variante.set(var_ux)
                self.actualizar_paneles(var_ux)
                
                valores_panel_ux = self.cb_panel.cget("values")
                if valores_panel_ux and pan_ux in valores_panel_ux:
                    self.cb_panel.set(pan_ux)
                    
                    self.lbl_pantalla_detectada.configure(
                        text=f"📺 {consola} | {var_ux} | {pan_ux}", 
                        text_color="#00FFFF"
                    )
                    
                    self.registrar_log(self.t("log_auto_adjust"), "success")
                    self.registrar_log(f"  ➤ {consola} > {variante} > {panel}", "title")
                else:
                    self.registrar_log(self.t("log_missing_panel").format(panel), "warning")

    # ================= MOTOR DE RENOMBRADO =================
    def generar_parametros_arranque(self, variante, os_target):
        if "4 Clone" in os_target or "dArkOS" in os_target: return "" 
        params = "alsa_path=SPK_HP "
        if variante.lower() == "soy_sauce": params += "gamma=0.8 "
        return params

    def procesar_copia_y_renombrado(self, ruta_origen, ruta_destino, consola, os_target, variante_ux, panel_ux):
        variante = self._mapa_variantes.get(variante_ux, variante_ux)
        panel_nombre = self._mapa_paneles.get(panel_ux, panel_ux)
        dtb_principal = None
        
        for item in ruta_origen.iterdir():
            if not item.is_file(): continue
            dest_name = item.name
            
            # --- RUTA 1: ArkOS 4 Clone ---
            if os_target == "ArkOS 4 Clone":
                if item.name.startswith("rk3326") and item.name.endswith(".dtb"):
                    dtb_principal = dest_name
                elif item.name.endswith("uboot.dtb"):
                    dest_name = "arkos4clone-uboot.dtb"
                    
            # --- RUTA 2: dArkOS RE ---
            elif os_target == "dArkOS RE":
                if item.name.startswith("rk3326") and item.name.endswith(".dtb"):
                    dest_name = f"rk3326-{consola.lower()}-linux.dtb"
                    dtb_principal = dest_name
                elif item.name.endswith("uboot.dtb"):
                    shutil.copy2(item, Path(ruta_destino) / "rg351v-uboot.dtb")
                    shutil.copy2(item, Path(ruta_destino) / "rg351p-uboot.dtb")
                    self.registrar_log(self.t("log_gen_uboot_dual"), "success")
                    continue 

            # --- RUTA 3: dArkOS ---
            elif os_target == "dArkOS":
                if item.name.startswith("rk3326") and item.name.endswith(".dtb"):
                    dest_name = "rk3326-rg351mp-linux.dtb"
                    dtb_principal = dest_name
                elif item.name.endswith("uboot.dtb"):
                    shutil.copy2(item, Path(ruta_destino) / "rg351mp-uboot.dtb")
                    shutil.copy2(item, Path(ruta_destino) / "rg351v-uboot.dtb")
                    shutil.copy2(item, Path(ruta_destino) / "rg351p-uboot.dtb")
                    self.registrar_log(self.t("log_gen_uboot_multi"), "success")
                    continue
                    
            # --- RUTA 4: ArkOS Original (Arranque Limpio) ---
            elif os_target == "ArkOS Original":
                if item.name.startswith("rk3326") and item.name.endswith(".dtb"):
                    dest_name = "rk3326-r35s-linux.dtb"
                    dtb_principal = dest_name
                elif item.name.endswith("uboot.dtb"):
                    # Duplicado simultáneo exigido por el panel original
                    shutil.copy2(item, Path(ruta_destino) / "rg351mp-kernel.dtb")
                    shutil.copy2(item, Path(ruta_destino) / "rg351p-kernel.dtb")
                    self.registrar_log(self.t("log_gen_kernel_dtb"), "success")
                    continue

            # --- COPIA FINAL ---
            shutil.copy2(item, Path(ruta_destino) / dest_name)
            
            if dest_name != item.name:
                self.registrar_log(self.t("log_copy_rename").format(item.name, dest_name), "warning")
            else:
                self.registrar_log(self.t("log_copy_intact").format(dest_name), "info")

        # === INYECCIÓN DE KERNEL ESPECÍFICO ===
        if os_target == "ArkOS Original":
            ruta_kernel = self.base_consolas / "kernel" / "original" / "Image"
            if ruta_kernel.exists():
                shutil.copy2(ruta_kernel, Path(ruta_destino) / "Image")
                self.registrar_log(self.t("log_inject_kernel"), "success")
            else:
                self.registrar_log(self.t("log_no_kernel"), "warning")
                
        return dtb_principal

    def procesar_boot_config(self, filepath, os_target, params_extra, dtb_name):
        try:
            with open(filepath, "r", encoding="utf-8") as f: contenido = f.read()
            modificado = False
            
            if "ArkOS" in os_target or "dArkOS" in os_target:
                if params_extra and "setenv bootargs" in contenido and "alsa_path=" not in contenido:
                    contenido = re.sub(r'(setenv bootargs ")', rf'\1{params_extra}', contenido)
                    modificado = True
                if dtb_name:
                    n_cont = re.sub(r'(load\s+mmc\s+1:1\s+\$\{dtb_loadaddr\}\s+)[^\s\n]+', rf'\g<1>{dtb_name}', contenido)
                    if n_cont != contenido: contenido = n_cont; modificado = True
                        
            if modificado:
                with open(filepath, "w", encoding="utf-8", newline='\n') as f: f.write(contenido)
                return True
            return False
        except Exception as e: raise Exception(f"Patching Error {filepath.name}: {e}")

    def generar_plantilla_arranque(self, output_dir, os_target, dtb_name, params_extra):
        freqs = "max_cpufreq=1296 boot_cpufreq=1248 max_gpufreq=520 max_ddrfreq=666"
        
        if os_target == "dArkOS RE":
            contenido = f"""odroidgoa-uboot-config

########################################################################
# Generado por Flux Digital Master Flasher (dArkOS RE)
########################################################################        

# Boot Arguments
setenv bootargs "root=LABEL=ROOTFS rootwait rw fsck.repair=yes net.ifnames=0 fbcon=rotate:0 console=/dev/ttyFIQ0 quiet splash consoleblank=0 vt.global_cursor_default=0 {freqs} {params_extra}"

# Booting
setenv loadaddr "0x02000000"
setenv initrd_loadaddr "0x01100000"
setenv dtb_loadaddr "0x01f00000"

load mmc 1:1 ${{loadaddr}} Image
load mmc 1:1 ${{initrd_loadaddr}} uInitrd

load mmc 1:1 ${{dtb_loadaddr}} {dtb_name}

booti ${{loadaddr}} ${{initrd_loadaddr}} ${{dtb_loadaddr}}
"""
            with open(Path(output_dir) / "boot.ini", "w", newline='\n') as f:
                f.write(contenido)
                
        elif os_target == "dArkOS":
            contenido = f"""odroidgoa-uboot-config

########################################################################
# Generado por Flux Digital Master Flasher (dArkOS)
########################################################################        

# Boot Arguments
setenv bootargs "root=/dev/mmcblk0p2 rootwait rw fsck.repair=yes net.ifnames=0 fbcon=rotate:0 console=/dev/ttyFIQ0 quiet splash consoleblank=0 vt.global_cursor_default=0 {freqs} {params_extra}"

# Booting
setenv loadaddr "0x02000000"
setenv initrd_loadaddr "0x01100000"
setenv dtb_loadaddr "0x01f00000"

load mmc 1:1 ${{loadaddr}} Image
load mmc 1:1 ${{initrd_loadaddr}} uInitrd

load mmc 1:1 ${{dtb_loadaddr}} {dtb_name}

booti ${{loadaddr}} ${{initrd_loadaddr}} ${{dtb_loadaddr}}
"""
            with open(Path(output_dir) / "boot.ini", "w", newline='\n') as f:
                f.write(contenido)

        elif os_target == "ArkOS Original":
            contenido = f"""odroidgoa-uboot-config

########################################################################
# Generado por Flux Digital Master Flasher (ArkOS Original)
# PANEL CHOOSER BYPASS - Arranque Directo Limpio
########################################################################

# Boot Arguments (Manteniendo el UUID oficial de ArkOS)
setenv bootargs "root=UUID='e139ce78-9841-40fe-8823-96a304a09859' rootwait rw fsck.repair=yes net.ifnames=0 fbcon=rotate:0 console=/dev/ttyFIQ0 quiet splash plymouth.ignore-serial-consoles consoleblank=0 {params_extra}"

# Booting
setenv loadaddr "0x02000000"
setenv initrd_loadaddr "0x01100000"
setenv dtb_loadaddr "0x01f00000"

# Carga de Kernel (Image) directo desde la raíz de la SD
load mmc 1:1 ${{loadaddr}} Image
load mmc 1:1 ${{initrd_loadaddr}} uInitrd

# Carga de DTB inyectado directo (evitando rutas de ScreenFiles)
load mmc 1:1 ${{dtb_loadaddr}} rk3326-r35s-linux.dtb

booti ${{loadaddr}} ${{initrd_loadaddr}} ${{dtb_loadaddr}}
"""
            with open(Path(output_dir) / "boot.ini", "w", newline='\n') as f:
                f.write(contenido)
                
        elif os_target == "ArkOS 4 Clone":
            contenido = f"""odroidgoa-uboot-config

########################################################################
# Generado por Flux Digital Master Flasher (ArkOS 4 Clone)
########################################################################        

# Boot Arguments
setenv bootargs "root=/dev/mmcblk0p2 rootwait rw fsck.repair=yes net.ifnames=0 fbcon=rotate:0 console=/dev/ttyFIQ0 quiet splash plymouth.ignore-serial-consoles consoleblank=0 {freqs} {params_extra}"

# Booting
setenv loadaddr "0x02000000"
setenv initrd_loadaddr "0x01100000"
setenv dtb_loadaddr "0x01f00000"

load mmc 1:1 ${{loadaddr}} Image
load mmc 1:1 ${{initrd_loadaddr}} uInitrd

load mmc 1:1 ${{dtb_loadaddr}} {dtb_name}

booti ${{loadaddr}} ${{initrd_loadaddr}} ${{dtb_loadaddr}}
"""
            with open(Path(output_dir) / "boot.ini", "w", newline='\n') as f:
                f.write(contenido)

    def flashear_archivos(self):
        sd_path = self.target_drive.get()
        if not os.path.exists(sd_path) or "Esperando" in sd_path or "Waiting" in sd_path or "No Detectada" in sd_path or "Not Detected" in sd_path:
            FluxDialog(self, self.t("btn_warning"), self.t("msg_sd_warning"), "warning")
            return

        consola, variante_ux, panel_ux, os_target = self.cb_consola.get(), self.cb_variante.get(), self.cb_panel.get(), self.cb_os.get()
        variante_real = self._mapa_variantes.get(variante_ux, variante_ux)
        panel_real = self._mapa_paneles.get(panel_ux, panel_ux)
        ruta_origen = self.base_consolas / consola / variante_real / panel_real
        
        if not ruta_origen.exists():
            FluxDialog(self, self.t("btn_error"), self.t("msg_base_dir_error").format(ruta_origen), "error")
            return

        self.limpiar_log()
        self.registrar_log(self.t("log_injecting").format(sd_path), "title")
        self.registrar_log(self.t("log_inject_info").format(os_target, consola, variante_ux, panel_ux), "info")

        try:
            self.registrar_log(self.t("log_transfer_dtb"), "info")
            dtb_principal = self.procesar_copia_y_renombrado(ruta_origen, sd_path, consola, os_target, variante_ux, panel_ux)
            
            self.registrar_log(self.t("log_patch_boot"), "info")
            params = self.generar_parametros_arranque(variante_real, os_target)
            
            modificado = False
            if Path(sd_path, "boot.ini").exists() and ("ArkOS" in os_target or "dArkOS" in os_target):
                modificado = self.procesar_boot_config(Path(sd_path, "boot.ini"), os_target, params, dtb_principal)
                
            self.registrar_log(self.t("log_process_ok"), "success")
            FluxDialog(self, self.t("btn_success"), self.t("msg_success_inject").format(os_target), "success")
        except Exception as e:
            self.registrar_log(self.t("log_critical_fail").format(e), "error")

    def exportar_zip(self):
        consola, variante_ux, panel_ux, os_target = self.cb_consola.get(), self.cb_variante.get(), self.cb_panel.get(), self.cb_os.get()
        variante_real = self._mapa_variantes.get(variante_ux, variante_ux)
        panel_real = self._mapa_paneles.get(panel_ux, panel_ux)
        ruta_origen = self.base_consolas / consola / variante_real / panel_real
        
        if not ruta_origen.exists(): return
        
        save_path = filedialog.asksaveasfilename(
            defaultextension=".zip",
            initialfile=f"Kit_{consola}_{os_target.replace(' ', '_')}_{variante_ux.replace(' ', '_')}_{panel_ux.replace(' ', '_')}.zip",
            filetypes=[("Archivos ZIP", "*.zip")]
        )
        if not save_path: return

        self.limpiar_log()
        self.registrar_log(self.t("log_pack_zip").format(os_target.upper()), "title")
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                dtb_principal = self.procesar_copia_y_renombrado(ruta_origen, temp_dir, consola, os_target, variante_ux, panel_ux)
                params = self.generar_parametros_arranque(variante_real, os_target)
                
                target_boot_dir = Path(temp_dir)
                self.generar_plantilla_arranque(target_boot_dir, os_target, dtb_principal or f"rk3326-{consola.lower()}-linux.dtb", params)
                
                shutil.make_archive(save_path[:-4] if save_path.endswith('.zip') else save_path, 'zip', temp_dir)
                
            self.registrar_log(self.t("log_zip_ok").format(Path(save_path).name), "success")
        except Exception as e:
            self.registrar_log(self.t("log_zip_fail").format(e), "error")

if __name__ == "__main__":
    app = FluxMasterFlasher()
    app.mainloop()