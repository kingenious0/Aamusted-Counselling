# How to Connect Your AAMUSTED Nodes (LAN Sync Guide)

This guide explains how to connect your **Admin**, **Secretary**, and **Counsellor** PCs so they can synchronize data without the internet.

## 📋 Prerequisites
1. All computers must be connected to the **same Wi-Fi** or **Network Router**.
2. The application must be running on all computers.

---

## 1️⃣ Find Your IP Address (Do this on EVERY PC)
Each computer needs to know its own "address" on the network.

### For Windows:
1. Open the application.
2. In the "Admin/Settings" or Startup console, look for text that says:  
   `Peer IP Address (Local Network): 192.168.x.x` (or similar).
3. OR, press `Windows Key + R`, type `cmd`, press Enter.
   - Type `ipconfig` and press Enter.
   - Look for **IPv4 Address**. It usually looks like `192.168.1.5` or `10.x.x.x`.

### For Mac:
1. Click the Apple Menu -> System Settings -> Network -> Wi-Fi.
2. Look for "IP Address".
3. OR, open Terminal and type `ipconfig getifaddr en0`.

---

## 2️⃣ Configure the Connection

You need to tell each computer who its "partner" is.

### Scenario: Admin PC ↔ Secretary PC
**(They need to talk to each other)**

**On the ADMIN PC:**
1. Go to **Settings** -> **Node Configuration**.
2. **Node Role:** Select `Admin Node`.
3. **Peer IP Address:** Enter the **Secretary PC's IP Address**.
4. Click **Update Node Settings**.

**On the SECRETARY PC:**
1. Go to **Settings** -> **Node Configuration**.
2. **Node Role:** Select `Secretary Node`.
3. **Peer IP Address:** Enter the **Admin PC's IP Address**.
4. Click **Update Node Settings**.

---

### Scenario: 3 PCs (Admin, Secretary, Counsellor)
If you have 3 PCs, you can chain them or point them to the "Main" DB.
*Simplest Logic:* Point everyone to the **Admin PC**.

**On SECRETARY PC:** Peer IP = `Admin IP`
**On COUNSELLOR PC:** Peer IP = `Admin IP`
**On ADMIN PC:** Peer IP = `Secretary IP` (or whomever it needs to pull updates from most often). 

*Note: The current simple sync connects strictly to ONE peer. For 3 PCs, A syncs with B, B syncs with C, eventually A gets C's data.*

---

## 3️⃣ Verify Connection
1. Change a setting or add a student on one PC.
2. Wait 60 seconds (automatic sync).
3. OR click **"Sync Now"** in the Admin Dashboard.
4. If the data appears on the other PC, **Success!** 🚀
