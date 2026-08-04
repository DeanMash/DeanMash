# ComeHome

Automated **30 / 60 / 90-day** client win-back for service businesses.

Personal WhatsApp check-ins (SMS fallback) that feel like a staff member wrote them — built for gyms, chiropractors, spas, salons, clinics and similar businesses in Zimbabwe and comparable markets.

**Pricing:** Studio **$800**/mo · Practice **$1,400**/mo · Chain **$2,000**/mo

## Get the code first

You must run commands **inside the cloned repo folder** (where `requirements.txt` and the `comehome` folder live). Running them from your user home folder will fail with “No such file” / “No module named comehome”.

### Windows (PowerShell)

```powershell
cd $HOME
git clone https://github.com/DeanMash/DeanMash.git
cd DeanMash
git checkout cursor/comehome-winback-system-34fa

python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m comehome
```

If `Activate.ps1` is blocked, run once:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then open:

- Marketing site: http://127.0.0.1:8080/
- Operator dashboard: http://127.0.0.1:8080/dashboard

Stop the server with `Ctrl+C`.

Already cloned? Just:

```powershell
cd path\to\DeanMash
git pull
git checkout cursor/comehome-winback-system-34fa
.\.venv\Scripts\Activate.ps1   # if you already made a venv
pip install -r requirements.txt
python -m comehome
```

### macOS / Linux

```bash
git clone https://github.com/DeanMash/DeanMash.git
cd DeanMash
git checkout cursor/comehome-winback-system-34fa
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m comehome
```

Optional lock (create a `.env` file in the repo root):

```env
COMEHOME_DASHBOARD_TOKEN=pick-a-secret
COMEHOME_PORT=8080
COMEHOME_WHATSAPP_MODE=demo
```

## CLI

```bash
python -m comehome seed   # reset demo business (Harare gym roster)
python -m comehome plan   # rebuild 30/60/90 queue
python -m comehome run    # send due messages (demo logs only)
python -m comehome web    # start server (default)
```

## Who it fits

Gyms, physiotherapists/chiropractors, spas, hair salons & barbers, dental & private clinics, optometry, sports academies, tutoring centres, nail/beauty studios, vet clinics, car-wash clubs — any business where last-visit silence means lost revenue.

## How it works

1. Import clients (name, phone, last visit, optional staff name)
2. ComeHome schedules WhatsApp copy at day 30, 60, and 90
3. Due messages send automatically; recovered clients stop the sequence
4. Dashboard shows lapsing clients, queue, and recoveries

Demo mode never hits live WhatsApp — it records sends for operators to review.
