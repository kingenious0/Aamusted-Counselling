# USTED Counselling Management System: Staff Handover Guide

Welcome to the **USTED Counselling Management System**. This guide will help you get started quickly on any machine.

---

## 🚀 How to Start the System

### 🖥️ For Windows Users:
1. Open the folder **AAMUSTED_Universal_Distribution → AAMUSTED_Windows_Installer**.
2. Double-click **USTED_Counselling_System.exe**.
3. The system will start, and your web browser will automatically open to the Dashboard.
4. *(Optional)* You can pin the `.exe` to your taskbar for quick access.

### 🍎 For Mac Users:
1. Open the folder **AAMUSTED_Universal_Distribution → AAMUSTED_Mac_Version**.
2. **Right-click** on **INSTALL_AND_RUN.command** and select **Open** (you may need to confirm once on first launch).
3. The system will set itself up and launch automatically in your browser.
4. From the second run onwards, just double-click **INSTALL_AND_RUN.command** to start.

---

## 🖥️ Using the System

- **Access URL**: `http://localhost:5000`
- **Default Login Credentials**:

| Role        | Username    | Password       |
|-------------|-------------|----------------|
| Admin       | `admin`     | `Admin123`     |
| Counsellor  | `counsellor`| `Counsellor123`|
| Secretary   | `secretary` | `Secretary123` |

> **Important:** Change all default passwords after first login via Admin → Settings → User Management.

- **Navigation**: Use the sidebar to access Students, Appointments, Reports, Statistics, and Settings.
- **Printing**: Click the **Print** button on any record to generate a professionally branded USTED document.

---

## ☁️ Cloud Sync

The system works **offline** but syncs automatically to the cloud when internet is available.

- **Status**: Check the "Sync Status" indicator at the bottom of the dashboard sidebar.
  - 🟢 **Green**: Data is synced to the cloud.
  - 🔴 **Red/Yellow**: No internet, or sync is disabled.
- **Enable/Disable**: Go to **Admin → Settings → Cloud Sync**.

---

## 🔗 Two-Computer Sync (Secretary ↔ Counsellor)

If running on two computers on the same network:
1. Note each machine's **IP address** (shown at startup on Mac; check via `ipconfig` on Windows).
2. On each machine, go to **Admin → Settings → Peer Sync** and enter the *other* machine's IP.

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| Browser doesn't open | Manually visit `http://localhost:5000` in Chrome or Edge |
| Data not syncing | Check internet connection; ensure "Sync Enabled" is ON in Settings |
| Need to restart | Close the app window and re-run the `.exe` (Windows) or `.command` (Mac) |
| Mac won't open `.command` | Right-click → Open → Confirm in the security dialog (first time only) |
| Login fails | Use default credentials above; or contact your system admin |

---

*USTED Counselling System — Version 2026 | Powered by AAMUSTED*
