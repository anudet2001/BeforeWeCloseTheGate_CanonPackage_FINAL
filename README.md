# Before We Close the Gate

## EP01 Final Production Package

**ตอน:** EP01 — นักสืบกับความกล้าที่อยู่ปลายเชือก  
**สถานะ Canon:** MASTER CANON  
**CCI:** 96/100  
**สถานะการผลิต:** UNLOCKED  
**สถานะการเผยแพร่:** READY FOR EXECUTIVE SIGN-OFF

## สารบัญ

- [ดาวน์โหลดและเปิดไฟล์สำคัญ](#ดาวน์โหลดและเปิดไฟล์สำคัญ)
- [ภาพรวมแพ็กเกจ](#ภาพรวมแพ็กเกจ)
- [โครงสร้างไฟล์](#โครงสร้างไฟล์)
- [คู่มือแยกตามทีม](#คู่มือแยกตามทีม)
- [เครื่องมือ Manifest](#เครื่องมือ-manifest)
- [การตรวจสอบแพ็กเกจ](#การตรวจสอบแพ็กเกจ)
- [Unit Tests](#unit-tests)
- [GitHub Actions](#github-actions)
- [นโยบาย SLA](#นโยบาย-sla)
- [กฎ Canon Lock](#กฎ-canon-lock)
- [สถานะสุดท้าย](#สถานะสุดท้าย)

## ดาวน์โหลดและเปิดไฟล์สำคัญ

ลิงก์ทั้งหมดด้านล่างเป็น relative path และใช้งานได้เมื่อเปิด README จากหน้า root ของ Repository บน GitHub

### Production และ Canon

- [ดาวน์โหลด Canon Package FINAL](Canon/BeforeWeCloseTheGate_CanonPackage_FINAL.zip)
- [เปิด Master Manifest](manifest.json)
- [เปิด JSON Schema](Documentation/manifest.schema.json)
- [เปิด Manifest Checksum](Documentation/manifest.sha256)

### Executive

- [ดาวน์โหลด Executive PMO FINAL](Executive/EP01_Executive_PMO_FINAL.xlsx)
- [ดาวน์โหลด Executive Presentation FINAL](Executive/EP01_Executive_Presentation_FINAL.pptx)

### Editing

- [ดาวน์โหลด Editor Shot List FINAL](Editing/EP01_Editor_ShotList_FINAL.csv)

### Tools, Tests และ CI

- [เปิด build_manifest.py](Tools/build_manifest.py)
- [เปิด verify_manifest.py](Tools/verify_manifest.py)
- [เปิด Unit Tests](tests/test_manifest_tools.py)
- [เปิด GitHub Actions Workflow](.github/workflows/verify-manifest.yml)
- [เปิด requirements.txt](requirements.txt)
- [เปิดคู่มือ Manifest Tools](Documentation/README_MANIFEST_TOOLS.md)

## ภาพรวมแพ็กเกจ

แพ็กเกจนี้รวมเอกสารและทรัพย์สินสำหรับการผลิต EP01 ตั้งแต่ Canon, Shot Breakdown, Image Prompt, Motion Prompt, Negative Prompt, การตัดต่อ, QC, SLA, RACI, Executive Dashboard ไปจนถึงเครื่องมือสร้างและตรวจ Manifest สำหรับ CI/CD

รายการสำคัญ:

- 11 ซีน และ 39 เฟรม
- Image Prompt, Motion Prompt และ Negative Prompt ครบ 39 เฟรม
- Canon Audit และ Canon Lock
- Executive PMO พร้อม SLA Dashboard และ RACI Matrix
- Editor Shot List
- JSON Schema และ SHA-256 checksums
- Unit Tests และ GitHub Actions แบบ Python matrix

## โครงสร้างไฟล์

```text
BeforeWeCloseTheGate_EP01_FINAL_PACKAGE/
├── README_FINAL.md
├── manifest.json
├── requirements.txt
├── Canon/
│   └── BeforeWeCloseTheGate_CanonPackage_FINAL.zip
├── Executive/
│   ├── EP01_Executive_PMO_FINAL.xlsx
│   └── EP01_Executive_Presentation_FINAL.pptx
├── Editing/
│   └── EP01_Editor_ShotList_FINAL.csv
├── Documentation/
│   ├── README_MANIFEST_TOOLS.md
│   ├── manifest.schema.json
│   └── manifest.sha256
├── Tools/
│   ├── build_manifest.py
│   └── verify_manifest.py
├── tests/
│   └── test_manifest_tools.py
└── .github/
    └── workflows/
        └── verify-manifest.yml
```

> รายการไฟล์จริง ขนาด และ SHA-256 checksum อยู่ใน [manifest.json](manifest.json)

## คู่มือแยกตามทีม

### ผู้บริหารและ Producer

1. เปิด [Executive PMO FINAL](Executive/EP01_Executive_PMO_FINAL.xlsx)
2. ตรวจ SLA Dashboard, Action Items, Owner, Escalation และ RACI
3. เปิด [Executive Presentation FINAL](Executive/EP01_Executive_Presentation_FINAL.pptx)
4. ลงนามอนุมัติก่อน Release

### ทีมเขียนบทและ Canon

1. เปิด [Canon Package FINAL](Canon/BeforeWeCloseTheGate_CanonPackage_FINAL.zip)
2. ใช้ Master Story Bible เป็น Canon ระดับสูงสุด
3. ตรวจ EP01 กับ Character, Location, Dialogue, Relationship, Clue และ Mystery Tracker
4. หากพบความขัดแย้ง ให้เปลี่ยนสถานะเป็น PRODUCTION LOCKED

### ทีมภาพและ Animation

1. ใช้ Production CSV ภายใน Canon Package
2. ใช้ Image Prompt, Motion Prompt และ Negative Prompt ตาม Frame ID
3. รักษามุมกล้อง เลนส์ แสง สี และ Character Design ตามตาราง
4. ตรวจ Character Drift ก่อนส่งต่อทีมตัดต่อ

### ทีมตัดต่อและ Audio

1. เปิด [Editor Shot List FINAL](Editing/EP01_Editor_ShotList_FINAL.csv)
2. เรียงช็อตตาม Scene และ Frame
3. เติม Timecode, BGM Cue, SFX และ Dialogue Track
4. ตรวจ Canon Checkpoint และความยาวตอนก่อน Final Render

### ทีม QA และ CI

1. ติดตั้ง dependencies จาก [requirements.txt](requirements.txt)
2. รัน Unit Tests
3. สร้าง Manifest ใหม่เมื่อไฟล์ในแพ็กเกจเปลี่ยนแปลง
4. รันตัวตรวจแบบ strict ก่อนส่งมอบ

## เครื่องมือ Manifest

### ติดตั้ง Dependencies

```bash
python -m pip install -r requirements.txt
```

### สร้าง Manifest และ Checksum

```bash
python Tools/build_manifest.py . --validate
```

รายงานแบบ JSON:

```bash
python Tools/build_manifest.py . --validate --json
```

ทดลองโดยไม่เขียนไฟล์:

```bash
python Tools/build_manifest.py . --dry-run --json
```

### ตรวจแพ็กเกจ

```bash
python Tools/verify_manifest.py . --strict
```

ตรวจ ZIP พร้อมรายงาน JSON:

```bash
python Tools/verify_manifest.py PACKAGE.zip --strict --json > verification-report.json
```

แสดง Exit Codes:

```bash
python Tools/verify_manifest.py PACKAGE.zip --show-exit-codes
```

รายละเอียดเพิ่มเติมอยู่ใน [Manifest Tools Guide](Documentation/README_MANIFEST_TOOLS.md)

## การตรวจสอบแพ็กเกจ

ตัวตรวจครอบคลุม:

- JSON syntax
- JSON Schema Draft 2020-12
- `file_count`
- ไฟล์ที่ระบุใน Manifest
- ไฟล์นอก Manifest ใน strict mode
- `size_bytes`
- SHA-256 ของทุก payload
- SHA-256 ของ `manifest.json` ผ่าน `Documentation/manifest.sha256`
- ZIP integrity

Exit Code หลัก:

- `0` ผ่านทั้งหมด
- `10` ไม่พบ Manifest
- `11` ไม่พบ Schema
- `12` JSON syntax ผิด
- `13` Schema validation ไม่ผ่าน
- `20` file count ไม่ตรง
- `21` ไฟล์หาย
- `22` พบไฟล์นอก Manifest
- `30` ขนาดไฟล์ไม่ตรง
- `31` SHA-256 ไม่ตรง
- `32` Manifest checksum ไม่ตรง
- `40` ZIP เสียหาย
- `50` Runtime/Internal error

## Unit Tests

รันชุดทดสอบ:

```bash
python -m unittest discover -s tests -v
```

ชุดทดสอบครอบคลุม:

- การสร้างรายการไฟล์และ `file_count`
- การตรวจแพ็กเกจที่ถูกต้อง
- การตรวจ payload ที่ถูกแก้ไข
- การตรวจ Manifest checksum mismatch
- การป้องกัน circular checksum

## GitHub Actions

Workflow อยู่ที่ [.github/workflows/verify-manifest.yml](.github/workflows/verify-manifest.yml)

รองรับ:

- Push
- Pull Request
- Manual Workflow Dispatch
- Python 3.10, 3.11, 3.12 และ 3.13
- Unit Tests
- Manifest Build บน temporary workspace
- Strict Verification
- JSON Reports แยกตาม Python version
- Artifact upload
- CI exit code enforcement

## นโยบาย SLA

- `Completed` งานเสร็จแล้ว
- `On Track` ยังไม่เข้าสู่ช่วงเสี่ยง
- `Pending` รอดำเนินการและยังไม่เกิน SLA
- `At Risk` อยู่ใน 20% สุดท้ายของ SLA
- `Overdue` เกินเวลาครบ SLA
- `Escalated` เกินวันและเวลา Escalation

## กฎ Canon Lock

ให้เปลี่ยนเป็น `PRODUCTION LOCKED` ทันทีเมื่อพบข้อใดข้อหนึ่ง:

- Canon Conflict
- Character, Dialogue, Relationship หรือ Location Conflict
- Lost Clue หรือ Mystery ไม่มีสถานะ
- Scene Audit มี FAIL
- CCI ต่ำกว่า 90

## สถานะสุดท้าย

```text
CANON STATUS      : MASTER CANON
CCI               : 96 / 100
RISK LEVEL        : LOW
PRODUCTION STATUS : UNLOCKED
RELEASE STATUS    : READY FOR EXECUTIVE SIGN-OFF
```

**Package Owner:** Before We Close the Gate Production Team  
**Classification:** Production Ready
