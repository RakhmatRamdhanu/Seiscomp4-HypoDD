import datetime
import sys
import os
import glob

# =============================================================================
# FUNGSI CORE: KONVERSI SATU FILE (VERSI ADAPTIF MLv/M/Mw)
# =============================================================================
def convert_seiscomp_to_hypodd(file_input, file_output):
    print(f"\n[SEDANG MEMPROSES] : {file_input} ...")
    
    events_processed = 0
    events_skipped = 0
    event_id_seq = 0
    current_meta = {}
    current_phases = []
    last_event_type = "UNKNOWN"
    state = "SEARCH_HEADER"

    try:
        with open(file_input, 'r', encoding='utf-8', errors='ignore') as f_in, \
             open(file_output, 'w', encoding='utf-8') as f_out:
            
            for line in f_in:
                line = line.strip()
                if not line: continue

                # 1. DETEKSI TIPE EVENT (A / M)
                if line.startswith("Alert") and "type" in line:
                    parts = line.split()
                    last_event_type = parts[-1].strip()
                    continue

                # 2. DETEKSI BLOK SOLUSI
                if "LOCSAT solution" in line:
                    if last_event_type == 'M':
                        current_meta = {}
                        current_phases = []
                        state = "READ_EVENT_DATA"
                    else:
                        events_skipped += 1
                        state = "SEARCH_HEADER"
                    continue

                # 3. BACA HEADER DATA (BAGIAN INI DIPERBAIKI)
                if state == "READ_EVENT_DATA":
                    # Cari tanda '=' untuk mendeteksi Magnitudo (M=, MLv=, Mw=, dll)
                    if "=" in line and "/" in line: # Indikasi ada Mag dan Tanggal
                        parts = line.split()
                        anchor_idx = -1
                        
                        # Cari posisi token yang mengandung "="
                        for i, p in enumerate(parts):
                            if "=" in p:
                                anchor_idx = i
                                break
                        
                        # Pastikan setelah Mag adalah Tanggal (ada karakter '/')
                        if anchor_idx != -1 and (anchor_idx + 1 < len(parts)) and "/" in parts[anchor_idx+1]:
                            try:
                                mag_str = parts[anchor_idx].split('=')[1] # Ambil angka setelah '='
                                date_str = parts[anchor_idx+1]
                                time_str = parts[anchor_idx+2]
                                lat_val = float(parts[anchor_idx+3])
                                lat_dir = parts[anchor_idx+4]
                                lon_val = float(parts[anchor_idx+5])
                                lon_dir = parts[anchor_idx+6]
                                depth_val = float(parts[anchor_idx+7])
                                
                                if lat_dir == 'S': lat_val = -lat_val
                                if lon_dir == 'W': lon_val = -lon_val
                                
                                # Fix tahun 2 digit
                                if len(date_str.split('/')[0]) == 2:
                                    date_str = '20' + date_str
                                
                                dt_str = f"{date_str} {time_str}"
                                origin_time = datetime.datetime.strptime(dt_str, "%Y/%m/%d %H:%M:%S.%f")
                                
                                current_meta = {
                                    'origin': origin_time, 'lat': lat_val, 'lon': lon_val,
                                    'depth': depth_val, 'mag': mag_str, 'rms': '0.000'
                                }
                                state = "SKIP_TABLE_HEADER"
                            except (ValueError, IndexError):
                                # Kalau format baris aneh, skip baris ini tapi tetap di state READ_EVENT_DATA
                                pass
                    continue

                if state == "SKIP_TABLE_HEADER":
                    if line.startswith("Stat"): state = "READ_PHASES"
                    continue

                # 4. BACA FASE & TULIS KE OUTPUT
                if state == "READ_PHASES":
                    if line.startswith("RMS-ERR:"):
                        # Pastikan metadata header berhasil diambil sebelum nulis
                        if not current_meta: 
                            state = "SEARCH_HEADER"
                            continue

                        parts = line.split(':')
                        if len(parts) > 1: current_meta['rms'] = parts[1].strip()
                        
                        event_id_seq += 1
                        ot = current_meta['origin']
                        
                        # Tulis Header HypoDD
                        header_line = (
                            f"# {ot.year:4d} {ot.month:2d} {ot.day:2d} "
                            f"{ot.hour:2d} {ot.minute:2d} {ot.second + ot.microsecond/1e6:5.2f} "
                            f"{current_meta['lat']:7.2f} {current_meta['lon']:8.2f} "
                            f"{current_meta['depth']:5.1f} {float(current_meta['mag']):4.1f} "
                            f"0.0 0.0 {float(current_meta['rms']):5.3f} {event_id_seq:9d}\n"
                        )
                        f_out.write(header_line)
                        
                        # Tulis Fase P & S
                        station_map = {}
                        for p in current_phases:
                            sta = p['stat']
                            if sta not in station_map: station_map[sta] = []
                            station_map[sta].append(p)
                        
                        for sta, arrivals in station_map.items():
                            arrivals.sort(key=lambda x: x['time'])
                            p_arrival = arrivals[0]
                            tt_p = (p_arrival['time'] - ot).total_seconds()
                            f_out.write(f"{sta.rjust(6)} {tt_p:10.2f}   1.000   P\n")
                            
                            if len(arrivals) > 1:
                                s_arrival = arrivals[1]
                                tt_s = (s_arrival['time'] - ot).total_seconds()
                                if tt_s > tt_p:
                                    f_out.write(f"{sta.rjust(6)} {tt_s:10.2f}   1.000   S\n")
                        
                        events_processed += 1
                        state = "SEARCH_HEADER"
                        continue
                    
                    try:
                        parts = line.split()
                        if len(parts) > 4:
                            stat_code = parts[0]
                            date_p = parts[2]
                            time_p = parts[3]
                            if len(date_p.split('/')[0]) == 2:
                                date_p = '20' + date_p
                            phase_dt = f"{date_p} {time_p}"
                            phase_time = datetime.datetime.strptime(phase_dt, "%Y/%m/%d %H:%M:%S.%f")
                            current_phases.append({'stat': stat_code, 'time': phase_time})
                    except:
                        continue

        print(f"   -> Sukses! {events_processed} event Type M dikonversi.")
        print(f"   -> {events_skipped} event Type A diabaikan.")
        print(f"   -> Output tersimpan di: {file_output}")
        return True

    except Exception as e:
        print(f"   [!] Gagal memproses file ini. Error: {e}")
        return False

# =============================================================================
# FUNGSI INTERAKTIF
# =============================================================================
if __name__ == "__main__":
    print("="*60)
    print("   SEISCOMP 4 to HYPODD ")
    print("="*60)
    
    # Mode Argumen (Otomatis)
    if len(sys.argv) >= 2:
        for f in sys.argv[1:]:
            bn = os.path.splitext(f)[0]
            convert_seiscomp_to_hypodd(f, bn + ".pha")
    
    # Mode Manual
    else:
        while True:
            fn = input("\n>> Ketik nama file input (.txt): ").strip()
            if not fn: break
            if os.path.exists(fn):
                bn = os.path.splitext(fn)[0]
                convert_seiscomp_to_hypodd(fn, bn + ".pha")
            else:
                print("   [!] File tidak ditemukan.")