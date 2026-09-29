# Manifest Tools Guide

คู่มือนี้อธิบายการสร้างและตรวจสอบ `manifest.json` สำหรับแพ็กเกจ FINAL

## ไฟล์เครื่องมือ

- `Tools/build_manifest.py` สแกนแพ็กเกจ คำนวณขนาดและ SHA-256 สร้าง `manifest.json` และ `Documentation/manifest.sha256`
- `Tools/verify_manifest.py` ตรวจ JSON Schema, manifest checksum, file count, ขนาดไฟล์, SHA-256 และ ZIP integrity
- `tests/test_manifest_tools.py` ชุด Unit Tests
- `.github/workflows/verify-manifest.yml` งาน CI สำหรับ Push, Pull Request และ Manual Run
- `requirements.txt` dependencies ของ Python

## ติดตั้ง

```bash
python -m pip install -r requirements.txt
```

## สร้าง Manifest

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

## ตรวจแพ็กเกจ

ตรวจโฟลเดอร์:

```bash
python Tools/verify_manifest.py . --strict
```

ตรวจ ZIP และสร้างรายงาน JSON:

```bash
python Tools/verify_manifest.py PACKAGE.zip --strict --json > verification-report.json
```

แสดง Exit Codes:

```bash
python Tools/verify_manifest.py PACKAGE.zip --show-exit-codes
```

## Unit Tests

```bash
python -m unittest discover -s tests -v
```

ครอบคลุมกรณีหลัก:

- สร้างรายการไฟล์และ `file_count`
- ตรวจแพ็กเกจที่ถูกต้อง
- ตรวจไฟล์ payload ถูกแก้ไข
- ตรวจ `manifest.json` ไม่ตรงกับ `manifest.sha256`
- ยืนยันว่า Manifest และ checksum ไม่ถูกนำมาคำนวณวนซ้ำ

## Exit Codes สำคัญ

- `0` ผ่านทั้งหมด
- `10` ไม่พบ `manifest.json`
- `11` ไม่พบ JSON Schema
- `12` JSON syntax ผิด
- `13` Schema validation ไม่ผ่าน
- `20` `file_count` ไม่ตรง
- `21` ไฟล์ที่ระบุหาย
- `22` พบไฟล์นอก Manifest ใน strict mode
- `30` ขนาดไฟล์ไม่ตรง
- `31` SHA-256 ของ payload ไม่ตรง
- `32` `manifest.sha256` หายหรือไม่ตรง
- `40` ZIP เสียหาย
- `50` Runtime/Internal error

## GitHub Actions

Workflow ทดสอบบน Python 3.10, 3.11, 3.12 และ 3.13 โดยทำตามลำดับ:

1. ติดตั้ง dependencies
2. รัน Unit Tests
3. คัดลอกแพ็กเกจไปยังพื้นที่ชั่วคราว
4. รัน `build_manifest.py --validate`
5. รัน `verify_manifest.py --strict --json`
6. อัปโหลด Build Report และ Verification Report
7. ส่ง Exit Code กลับให้ CI

> Workflow ใช้สำเนาชั่วคราวในการทดสอบ build เพื่อไม่แก้ไขไฟล์ใน working tree
