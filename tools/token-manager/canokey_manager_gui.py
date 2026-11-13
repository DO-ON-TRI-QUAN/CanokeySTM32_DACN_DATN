import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import json

try:
    from fido2.hid import CtapHidDevice
    from fido2.ctap2 import Ctap2, ClientPin
    from fido2.ctap import CtapError
    FIDO2_AVAILABLE = True
except ImportError:
    FIDO2_AVAILABLE = False


class MockCtap2Device:
    """Giả lập thiết bị CanoKey STM32 để test giao diện & logic khi chưa cắm kit phần cứng."""
    def __init__(self):
        self.pin = None
        self.retries = 8
        self.aaguid = "7c8a9e2b-4f10-4b8d-9a21-6c5e3f8d1092"

    def get_info_dict(self):
        return {
            "Device Mode": "SIMULATED (No Physical USB Detected)",
            "Protocols": ["FIDO_2_0", "FIDO_2_1_PRE", "U2F_V2"],
            "AAGUID": self.aaguid,
            "Extensions": ["credProtect", "hmac-secret"],
            "Options": {
                "rk": True,
                "up": True,
                "plat": False,
                "clientPin": self.pin is not None
            },
            "Max Message Size": "1200 bytes",
            "PIN Protocols": [1, 2],
            "PIN Status": f"Configured ({self.retries} retries left)" if self.pin else "Not Set"
        }

    def set_pin(self, new_pin):
        if self.pin is not None:
            raise Exception("PIN is already set. Use Change PIN instead.")
        if len(new_pin) < 4:
            raise Exception("CTAP2_ERR_PIN_POLICY_VIOLATION: PIN must be at least 4 characters.")
        self.pin = new_pin
        self.retries = 8

    def change_pin(self, old_pin, new_pin):
        if self.pin is None:
            raise Exception("CTAP2_ERR_PIN_NOT_SET: No PIN configured.")
        if old_pin != self.pin:
            self.retries -= 1
            raise Exception(f"CTAP2_ERR_PIN_INVALID: Wrong current PIN ({self.retries} retries left).")
        if len(new_pin) < 4:
            raise Exception("CTAP2_ERR_PIN_POLICY_VIOLATION: New PIN must be at least 4 characters.")
        self.pin = new_pin
        self.retries = 8

    def reset(self):
        self.pin = None
        self.retries = 8


class CanoKeyManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CanoKey STM32 - USB Security Token Manager")
        self.root.geometry("680x520")
        self.root.resizable(False, False)
        self.root.configure(bg="#f4f6f9")

        self.mock_device = MockCtap2Device()
        self.is_mock = True
        self.ctap2 = None

        self._build_ui()
        self.refresh_device()

    def _build_ui(self):
        header = tk.Frame(self.root, bg="#1e293b", height=70)
        header.pack(fill="x")
        tk.Label(
            header, text="CanoKey STM32 Security Token Manager",
            font=("Segoe UI", 15, "bold"), fg="white", bg="#1e293b"
        ).pack(side="left", padx=20, pady=18)

        self.status_badge = tk.Label(
            header, text="Checking...", font=("Segoe UI", 9, "bold"),
            fg="#1e293b", bg="#facc15", padx=10, pady=4
        )
        self.status_badge.pack(side="right", padx=20)

        btn_frame = tk.Frame(self.root, bg="#f4f6f9", pady=15)
        btn_frame.pack(fill="x", padx=20)

        btn_style = {"font": ("Segoe UI", 10, "bold"), "width": 16, "pady": 8, "bd": 0, "cursor": "hand2"}

        tk.Button(
            btn_frame, text="🔄 Refresh / GetInfo", bg="#2563eb", fg="white",
            command=self.refresh_device, **btn_style
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            btn_frame, text="🔑 Set Initial PIN", bg="#059669", fg="white",
            command=self.handle_set_pin, **btn_style
        ).grid(row=0, column=1, padx=5)

        tk.Button(
            btn_frame, text="✏️ Change PIN", bg="#d97706", fg="white",
            command=self.handle_change_pin, **btn_style
        ).grid(row=0, column=2, padx=5)

        tk.Button(
            btn_frame, text="⚠️ Factory Reset", bg="#dc2626", fg="white",
            command=self.handle_factory_reset, **btn_style
        ).grid(row=0, column=3, padx=5)

        info_frame = tk.LabelFrame(
            self.root, text=" Device Information (CTAP2 authenticatorGetInfo) ",
            font=("Segoe UI", 10, "bold"), bg="white", fg="#334155", padx=15, pady=10
        )
        info_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        self.info_text = tk.Text(
            info_frame, font=("Consolas", 10), bg="#f8fafc", fg="#0f172a",
            bd=1, relief="solid", padx=10, pady=10, state="disabled"
        )
        self.info_text.pack(fill="both", expand=True)

        self.log_var = tk.StringVar(value="Ready.")
        footer = tk.Label(
            self.root, textvariable=self.log_var, font=("Segoe UI", 9),
            bg="#e2e8f0", fg="#334155", anchor="w", padx=15, pady=6
        )
        footer.pack(fill="x", side="bottom")

    def _update_info_box(self, content_dict):
        self.info_text.config(state="normal")
        self.info_text.delete("1.0", tk.END)
        formatted = json.dumps(content_dict, indent=4, ensure_ascii=False)
        self.info_text.insert(tk.END, formatted)
        self.info_text.config(state="disabled")

    def refresh_device(self):
        self.ctap2 = None
        if FIDO2_AVAILABLE:
            devices = list(CtapHidDevice.list_devices())
            if devices:
                try:
                    self.ctap2 = Ctap2(devices[0])
                    self.is_mock = False
                except Exception as e:
                    self.log_var.set(f"Error connecting to HID device: {e}")

        if not self.is_mock and self.ctap2:
            self.status_badge.config(text="● CONNECTED (USB HID)", bg="#4ade80", fg="#064e3b")
            info = self.ctap2.get_info()
            client_pin = ClientPin(self.ctap2)
            try:
                retries, _ = client_pin.get_pin_retries()
                pin_status = f"Configured ({retries} retries left)"
            except CtapError:
                pin_status = "Not Set"

            data = {
                "Device Mode": "PHYSICAL HARDWARE (CanoKey STM32)",
                "Protocols": list(info.versions),
                "AAGUID": info.aaguid.hex(),
                "Extensions": list(info.extensions or []),
                "Options": dict(info.options or {}),
                "Max Message Size": f"{info.max_msg_size} bytes",
                "PIN Protocols": list(info.pin_uv_protocols or []),
                "PIN Status": pin_status
            }
            self._update_info_box(data)
            self.log_var.set("Connected to physical FIDO2 USB Security Token.")
        else:
            self.is_mock = True
            self.status_badge.config(text="● SIMULATION MODE", bg="#facc15", fg="#422006")
            self._update_info_box(self.mock_device.get_info_dict())
            self.log_var.set("No physical USB token found. Running in Simulation Mode.")

    def handle_set_pin(self):
        new_pin = simpledialog.askstring("Set Initial PIN", "Enter new PIN (min 4 chars):", show="*")
        if not new_pin:
            return
        confirm_pin = simpledialog.askstring("Confirm PIN", "Re-enter new PIN:", show="*")
        if new_pin != confirm_pin:
            messagebox.showerror("Error", "PINs do not match!")
            return

        try:
            if self.is_mock:
                self.mock_device.set_pin(new_pin)
            else:
                ClientPin(self.ctap2).set_pin(new_pin)
            messagebox.showinfo("Success", "Initial PIN configured successfully!")
            self.refresh_device()
        except Exception as e:
            messagebox.showerror("CTAP2 Error", str(e))

    def handle_change_pin(self):
        old_pin = simpledialog.askstring("Change PIN", "Enter current PIN:", show="*")
        if not old_pin:
            return
        new_pin = simpledialog.askstring("Change PIN", "Enter new PIN (min 4 chars):", show="*")
        if not new_pin:
            return
        confirm_pin = simpledialog.askstring("Confirm New PIN", "Re-enter new PIN:", show="*")
        if new_pin != confirm_pin:
            messagebox.showerror("Error", "New PINs do not match!")
            return

        try:
            if self.is_mock:
                self.mock_device.change_pin(old_pin, new_pin)
            else:
                ClientPin(self.ctap2).change_pin(old_pin, new_pin)
            messagebox.showinfo("Success", "PIN changed successfully!")
            self.refresh_device()
        except Exception as e:
            messagebox.showerror("CTAP2 Error", str(e))

    def handle_factory_reset(self):
        confirm = messagebox.askyesno(
            "Confirm Factory Reset",
            "WARNING: Factory Reset will erase ALL FIDO2 credentials and PIN on the token!\n\n"
            "Note: On CanoKey hardware, reset must be executed within 10 seconds of plugging in the USB "
            "and requires pressing the physical button.\n\nProceed?"
        )
        if not confirm:
            return

        if self.is_mock:
            self.mock_device.reset()
            messagebox.showinfo("Success", "Simulated Factory Reset completed!")
            self.refresh_device()
        else:
            self.log_var.set("Waiting for physical button press on USB Token to confirm Factory Reset...")
            def run_reset():
                try:
                    self.ctap2.reset()
                    self.root.after(0, lambda: messagebox.showinfo("Success", "Hardware Factory Reset completed!"))
                    self.root.after(0, self.refresh_device)
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Reset Failed", f"{e}\n(Try unplugging/replugging USB and reset within 10s)"))
                    self.root.after(0, lambda: self.log_var.set("Factory Reset failed."))
            threading.Thread(target=run_reset, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = CanoKeyManagerApp(root)
    root.mainloop()
