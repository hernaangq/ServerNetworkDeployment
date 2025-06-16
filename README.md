# ServerNetworkDeployment 🖥️

A deployment and server configuration project created for the CDPS course at ETSIT‑UPM (2023–2024).

---

## 🔧 Tech Stack

- **Python 3**: Used for automating VM creation, configuration, and management tasks.
- **QEMU/KVM**: Emulation and virtualization tools for launching and managing virtual machines (`qemu-img`, `virsh`, `virt-copy-in`, `virt-edit`).
- **libvirt**: Virtualization API used via `virsh` to manage VM lifecycle (define, start, shutdown, undefine).
- **Brctl & Ifconfig**: Tools for creating and managing Linux bridges for VM networking.
- **XML (via lxml)**: Configuration of virtual machines using XML descriptors (VM hardware settings, bridges).
- **Shell Utilities**: Various commands (`cp`, `rm`, `xterm`, etc.) invoked using `subprocess.call`.
- **Xterm**: Used to spawn VM consoles for interaction.
- **Linux Networking**: Manual configuration of `/etc/hosts`, `/etc/network/interfaces`, routing via `ip route`.

---

## 🛠️ Features

* Automated provisioning of one or more servers
* Configuration of services (e.g., web server, database, API endpoint)
* Modular and reusable scripts for easy redeployment

---

## 📫 Contact

For questions, feedback, or collaboration:

* 📧 Email: [hernangarqui@gmail.com](mailto:hernangarqui@gmail.com)
* 💼 LinkedIn: [Hernán García Quijano](https://www.linkedin.com/in/hernan-garcia-quijano)


