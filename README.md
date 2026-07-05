<div align="center">
  <img src="https://i.ibb.co/8qt394G/imagen-2026-07-04-225134530.png" alt="Flux Digital - Master Flasher Portada" width="800">
</div>

<br>

> ### 🎯 Project Overview
> This project aims to serve as a dynamic and reliable starting point for testing—or permanently deploying—your favorite custom operating system on any **RK3326-based handheld**. 
>
> 🧪 **Hardware Validation:** Primary forensic and boot testing is strictly conducted on an **R36S "Soy Sauce"** model equipped with a **Panel 2** display.

<br>

### 🚀 How to Use
1. **Flash the OS:** Install your preferred system or `.img` onto a microSD card using tools like [Rufus](https://rufus.ie/), [BalenaEtcher](https://balena.io/etcher/), or Win32DiskImager.
2. **Prepare the DTB:** Keep the freshly flashed microSD card connected to your PC. Add or identify your console's specific `.dtb` file using the app's Forensic Inspector.
3. **Configure & Deploy:** On the left panel, select your **Target OS Environment** and hardware profile. You can deploy directly to the microSD card (**⚡ INJECT SYSTEM**), export the files as a ZIP (**📦 PACKAGE DISTRIBUTION KIT**), or safely clone your current drive (**💾 SYSTEM BACKUP**).
4. **Play:** Insert the microSD card into your handheld console, power it on, and enjoy! 🎮

<br>

### 💾 System Backup (1:1 RAW Image)
Easily create a perfect bit-by-bit backup of your original stock microSD or your newly customized setup. The app directly reads the physical drive to securely clone all partitions into a single `.img` file for safe keeping (Requires Administrator privileges).

<br>

### 🌟 Supported Systems & Special Thanks
This project wouldn't be possible without the extensive research, kernel development, and display panel mapping provided by the community. A massive shoutout to the maintainers of the following custom firmwares:

* ![ArkOS 4 Clone](https://img.shields.io/badge/ArkOS_4_Clone-007FFF?style=for-the-badge) 
  [lcdyk0517/arkos4clone](https://github.com/lcdyk0517/arkos4clone)
* ![ArkOS R3XS](https://img.shields.io/badge/ArkOS_R3XS-00FFFF?style=for-the-badge&logoColor=black) 
  [AeolusUX/ArkOS-R3XS](https://github.com/AeolusUX/ArkOS-R3XS)
* ![dArkOS RE](https://img.shields.io/badge/dArkOS_RE_R36-007FFF?style=for-the-badge) 
  [southoz/dArkOSRE-R36](https://github.com/southoz/dArkOSRE-R36)
* ![dArkOS](https://img.shields.io/badge/dArkOS_(RG351MP)-00FFFF?style=for-the-badge&logoColor=black) 
  [christianhaitian/dArkOS](https://github.com/christianhaitian/dArkOS)
