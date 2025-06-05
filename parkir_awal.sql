--
-- PostgreSQL database dump
--

-- Started on 2018-05-26 10:09:35

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

--
-- TOC entry 856 (class 2612 OID 16386)
-- Name: plpgsql; Type: PROCEDURAL LANGUAGE; Schema: -; Owner: -
--

CREATE PROCEDURAL LANGUAGE plpgsql;


SET search_path = public, pg_catalog;

--
-- TOC entry 236 (class 1255 OID 16396)
-- Dependencies: 856 6
-- Name: on_audit(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION on_audit() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 
  DECLARE
      POTONG		INTEGER;
      MASUK 		TIMESTAMP;
      BAYAR		INTEGER;
      CONFIG 		RECORD;
      TINTERVAL		INTERVAL;
      WAKTU_TARIF	INTERVAL;
  BEGIN
    SELECT INTO CONFIG * FROM NX_AUDIT LIMIT 1;

    IF (DATE_PART('DAY', CONFIG.last)<>DATE_PART('DAY',now())) THEN
      CONFIG.real  := 0;
      CONFIG.audit := 0;
    END IF;

    IF (TG_OP='INSERT') THEN
      IF (NEW.status=0) THEN
        IF (NEW.status_transaksi='0') and (NEW.bayar_keluar > 0) and (NEW.status_transaksi<>'32') THEN
          IF (NEW.bayar_keluar < CONFIG.limit_value) THEN
            CONFIG.real := CONFIG.real + NEW.bayar_keluar;
	    SELECT INTO TINTERVAL (select (tarif.interval::text || ' MINUTES')::interval+'10 MINUTES' from tarif where id_mobil=NEW.id_kendaraan);
            IF ((((CONFIG.audit+NEW.bayar_keluar)/CONFIG.real)*100)<CONFIG.ratio) THEN
              CONFIG.audit := CONFIG.audit + NEW.bayar_keluar;
              insert into parkir_transaksi (id,no_pol, id_kendaraan, status, id_pintu_masuk,
							id_pintu_keluar, waktu_masuk, waktu_keluar, id_op_masuk,
							id_op_keluar, id_shift_masuk, id_shift_keluar, kategori,
							status_transaksi, bayar_masuk, bayar_keluar, jenis_system,
							tanggal, pic_driver_masuk,
							pic_driver_keluar, pic_no_pol_masuk, pic_no_pol_keluar,
							sinkron, adm, alasan, pmlogin, pklogin, upload, manual,
							veri_kode, veri_check, veri_adm, veri_date, denda,
							extra_bayar, no_barcode, jenis_langganan, post_pay, reff_kode)  
							values(NEW.id, NEW.no_pol, NEW.id_kendaraan,NEW.status, NEW.id_pintu_masuk, 
							NEW.id_pintu_keluar, NEW.waktu_masuk, NEW.waktu_keluar, NEW.id_op_masuk, 
							NEW.id_op_keluar, NEW.id_shift_masuk, NEW.id_shift_keluar, NEW.kategori, 
							NEW.status_transaksi, NEW.bayar_masuk, NEW.bayar_keluar, NEW.jenis_system, 
							NEW.tanggal, NEW.pic_driver_masuk, 
							NEW.pic_driver_keluar, NEW.pic_no_pol_masuk, NEW.pic_no_pol_keluar, 
							NEW.sinkron, NEW.adm, NEW.alasan, NEW.pmlogin, NEW.pklogin, NEW.upload, NEW.manual, 
							NEW.veri_kode, NEW.veri_check, NEW.veri_adm, NEW.veri_date, NEW.denda, 
							NEW.extra_bayar, NEW.no_barcode, NEW.jenis_langganan, NEW.post_pay, NEW.reff_kode);
            ELSE
              IF config.db='time.db' THEN
	  	IF (age(NEW.waktu_keluar,NEW.waktu_masuk)>TINTERVAL)  and (NEW.status_transaksi<>'32') THEN
			SELECT INTO POTONG (select tarif from tarif where id_mobil=NEW.id_kendaraan);
			SELECT INTO WAKTU_TARIF (select (tarif.waktu_tarif::text || ' MINUTES')::interval from tarif where id_mobil=NEW.id_kendaraan);
			SELECT INTO BAYAR (select (CASE WHEN bayar_masuk is null then 0 ELSE bayar_masuk END) + bayar_keluar from transaksi_parkir where id=NEW.id and no_pol=NEW.no_pol and waktu_masuk=NEW.waktu_masuk) - POTONG;
			SELECT INTO MASUK (select waktu_masuk from transaksi_parkir where id=NEW.id and no_pol=NEW.no_pol and waktu_masuk=NEW.waktu_masuk) + WAKTU_TARIF;
			CONFIG.audit := CONFIG.audit + BAYAR;
			insert into parkir_transaksi (id,no_pol, id_kendaraan, status, id_pintu_masuk,
							id_pintu_keluar, waktu_masuk, waktu_keluar, id_op_masuk,
							id_op_keluar, id_shift_masuk, id_shift_keluar, kategori,
							status_transaksi, bayar_masuk, bayar_keluar, jenis_system,
							tanggal, pic_driver_masuk,
							pic_driver_keluar, pic_no_pol_masuk, pic_no_pol_keluar,
							sinkron, adm, alasan, pmlogin, pklogin, upload, manual,
							veri_kode, veri_check, veri_adm, veri_date, denda,
							extra_bayar, no_barcode, jenis_langganan, post_pay, reff_kode)  
							values(NEW.id, NEW.no_pol, NEW.id_kendaraan, NEW.status, NEW.id_pintu_masuk, 
							NEW.id_pintu_keluar, MASUK, NEW.waktu_keluar, NEW.id_op_masuk, 
							NEW.id_op_keluar, NEW.id_shift_masuk, NEW.id_shift_keluar, NEW.kategori, 
							NEW.status_transaksi, NEW.bayar_masuk, BAYAR, NEW.jenis_system, 
							NEW.tanggal, NEW.pic_driver_masuk, 
							NEW.pic_driver_keluar, NEW.pic_no_pol_masuk, NEW.pic_no_pol_keluar, 
							NEW.sinkron, NEW.adm, NEW.alasan, NEW.pmlogin, NEW.pklogin, NEW.upload, NEW.manual, 
							NEW.veri_kode, NEW.veri_check, NEW.veri_adm, NEW.veri_date, NEW.denda, 
							NEW.extra_bayar, NEW.no_barcode, NEW.jenis_langganan, NEW.post_pay, NEW.reff_kode);
	  	ELSE 
	  	  IF  (NEW.status_transaksi<>'32') THEN
			IF (NEW.bayar_keluar > 0) and (NEW.bayar_keluar < CONFIG.limit_value) THEN
				CONFIG.audit := CONFIG.audit + NEW.bayar_keluar;
			END IF;
			insert into parkir_transaksi (id,no_pol, id_kendaraan, status, id_pintu_masuk,
							id_pintu_keluar, waktu_masuk, waktu_keluar, id_op_masuk,
							id_op_keluar, id_shift_masuk, id_shift_keluar, kategori,
							status_transaksi, bayar_masuk, bayar_keluar, jenis_system,
							tanggal, pic_driver_masuk,
							pic_driver_keluar, pic_no_pol_masuk, pic_no_pol_keluar,
							sinkron, adm, alasan, pmlogin, pklogin, upload, manual,
							veri_kode, veri_check, veri_adm, veri_date, denda,
							extra_bayar, no_barcode, jenis_langganan, post_pay, reff_kode)  
							values(NEW.id, NEW.no_pol, NEW.id_kendaraan,NEW.status, NEW.id_pintu_masuk, 
							NEW.id_pintu_keluar, NEW.waktu_masuk, NEW.waktu_keluar, NEW.id_op_masuk, 
							NEW.id_op_keluar, NEW.id_shift_masuk, NEW.id_shift_keluar, NEW.kategori, 
							NEW.status_transaksi, NEW.bayar_masuk, NEW.bayar_keluar, NEW.jenis_system, 
							NEW.tanggal, NEW.pic_driver_masuk, 
							NEW.pic_driver_keluar, NEW.pic_no_pol_masuk, NEW.pic_no_pol_keluar, 
							NEW.sinkron, NEW.adm, NEW.alasan, NEW.pmlogin, NEW.pklogin, NEW.upload, NEW.manual, 
							NEW.veri_kode, NEW.veri_check, NEW.veri_adm, NEW.veri_date, NEW.denda, 
							NEW.extra_bayar, NEW.no_barcode, NEW.jenis_langganan, NEW.post_pay, NEW.reff_kode);
		  END IF;
		END IF;
	      ELSE
	        IF (config.db='empty.db') AND (NEW.status_transaksi<>'32') THEN
	          insert into parkir_transaksi (id,no_pol, id_kendaraan, status, id_pintu_masuk,
							id_pintu_keluar, waktu_masuk, waktu_keluar, id_op_masuk,
							id_op_keluar, id_shift_masuk, id_shift_keluar, kategori,
							status_transaksi, bayar_masuk, bayar_keluar, jenis_system,
							tanggal, pic_driver_masuk,
							pic_driver_keluar, pic_no_pol_masuk, pic_no_pol_keluar,
							sinkron, adm, alasan, pmlogin, pklogin, upload, manual,
							veri_kode, veri_check, veri_adm, veri_date, denda,
							extra_bayar, no_barcode, jenis_langganan, post_pay, reff_kode)  
							values(NEW.id, NEW.no_pol, NEW.id_kendaraan,NEW.status, NEW.id_pintu_masuk, 
							NEW.id_pintu_keluar, NEW.waktu_masuk, NEW.waktu_keluar, NEW.id_op_masuk, 
							NEW.id_op_keluar, NEW.id_shift_masuk, NEW.id_shift_keluar, NEW.kategori, 
							NEW.status_transaksi, 0, 0, NEW.jenis_system, 
							NEW.tanggal, NEW.pic_driver_masuk, 
							NEW.pic_driver_keluar, NEW.pic_no_pol_masuk, NEW.pic_no_pol_keluar, 
							NEW.sinkron, NEW.adm, NEW.alasan, NEW.pmlogin, NEW.pklogin, NEW.upload, NEW.manual, 
							'0123456789', 1, '0001', NEW.veri_date, NEW.denda, 
							NEW.extra_bayar, NEW.no_barcode, NEW.jenis_langganan, NEW.post_pay, NEW.reff_kode);
  	        ELSE
 	        END IF;
	      END IF;
            END IF; 
          END IF;
        ELSE
          IF (NEW.status_transaksi<>'32') THEN 
            insert into parkir_transaksi (  id,no_pol, id_kendaraan, status, id_pintu_masuk,
									id_pintu_keluar, waktu_masuk, waktu_keluar, id_op_masuk,
									id_op_keluar, id_shift_masuk, id_shift_keluar, kategori,
									status_transaksi, bayar_masuk, bayar_keluar, jenis_system,
									tanggal, pic_driver_masuk,
									pic_driver_keluar, pic_no_pol_masuk, pic_no_pol_keluar,
									sinkron, adm, alasan, pmlogin, pklogin, upload, manual,
									veri_kode, veri_check, veri_adm, veri_date, denda,
									extra_bayar, no_barcode, jenis_langganan, post_pay, reff_kode)  
									values( 
									NEW.id, NEW.no_pol, NEW.id_kendaraan, NEW.status, NEW.id_pintu_masuk, 
									NEW.id_pintu_keluar, NEW.waktu_masuk, NEW.waktu_keluar, NEW.id_op_masuk, 
									NEW.id_op_keluar, NEW.id_shift_masuk, NEW.id_shift_keluar, NEW.kategori, 
									NEW.status_transaksi, NEW.bayar_masuk, NEW.bayar_keluar, NEW.jenis_system, 
									NEW.tanggal, NEW.pic_driver_masuk, 
									NEW.pic_driver_keluar, NEW.pic_no_pol_masuk, NEW.pic_no_pol_keluar, 
									NEW.sinkron, NEW.adm, NEW.alasan, NEW.pmlogin, NEW.pklogin, NEW.upload, NEW.manual, 
									NEW.veri_kode, NEW.veri_check, NEW.veri_adm, NEW.veri_date, NEW.denda, 
									NEW.extra_bayar, NEW.no_barcode, NEW.jenis_langganan, NEW.post_pay, NEW.reff_kode);
          END IF;
        END IF;
      ELSE 
          insert into parkir_transaksi (    id,no_pol, id_kendaraan, status, id_pintu_masuk,
									id_pintu_keluar, waktu_masuk, waktu_keluar, id_op_masuk,
								        id_op_keluar, id_shift_masuk, id_shift_keluar, kategori,
									status_transaksi, bayar_masuk, bayar_keluar, jenis_system,
									tanggal, pic_driver_masuk,
									pic_driver_keluar, pic_no_pol_masuk, pic_no_pol_keluar,
									sinkron, adm, alasan, pmlogin, pklogin, upload, manual,
									veri_kode, veri_check, veri_adm, veri_date, denda,
									extra_bayar, no_barcode, jenis_langganan, post_pay, reff_kode)  
									values( 
									NEW.id, NEW.no_pol, NEW.id_kendaraan, NEW.status, NEW.id_pintu_masuk, 
									NEW.id_pintu_keluar, NEW.waktu_masuk, NEW.waktu_keluar, NEW.id_op_masuk, 
									NEW.id_op_keluar, NEW.id_shift_masuk, NEW.id_shift_keluar, NEW.kategori, 
									NEW.status_transaksi, NEW.bayar_masuk, NEW.bayar_keluar, NEW.jenis_system, 
									NEW.tanggal, NEW.pic_driver_masuk, 
									NEW.pic_driver_keluar, NEW.pic_no_pol_masuk, NEW.pic_no_pol_keluar, 
									NEW.sinkron, NEW.adm, NEW.alasan, NEW.pmlogin, NEW.pklogin, NEW.upload, NEW.manual, 
									NEW.veri_kode, NEW.veri_check, NEW.veri_adm, NEW.veri_date, NEW.denda, 
									NEW.extra_bayar, NEW.no_barcode, NEW.jenis_langganan, NEW.post_pay, NEW.reff_kode);
      END IF;
    END IF;

    IF (TG_OP='UPDATE') THEN
      IF NEW.status=1 THEN
        delete from parkir_transaksi where id= NEW.id and waktu_masuk= NEW.waktu_masuk;
        insert into parkir_transaksi (    id,no_pol, id_kendaraan, status, id_pintu_masuk,
									id_pintu_keluar, waktu_masuk, waktu_keluar, id_op_masuk,
								        id_op_keluar, id_shift_masuk, id_shift_keluar, kategori,
									status_transaksi, bayar_masuk, bayar_keluar, jenis_system,
									tanggal, pic_driver_masuk,
									pic_driver_keluar, pic_no_pol_masuk, pic_no_pol_keluar,
									sinkron, adm, alasan, pmlogin, pklogin, upload, manual,
									veri_kode, veri_check, veri_adm, veri_date, denda,
									extra_bayar, no_barcode, jenis_langganan, post_pay, reff_kode)  
									values( 
									NEW.id, NEW.no_pol, NEW.id_kendaraan, NEW.status, NEW.id_pintu_masuk, 
									NEW.id_pintu_keluar, NEW.waktu_masuk, NEW.waktu_keluar, NEW.id_op_masuk, 
									NEW.id_op_keluar, NEW.id_shift_masuk, NEW.id_shift_keluar, NEW.kategori, 
									NEW.status_transaksi, NEW.bayar_masuk, NEW.bayar_keluar, NEW.jenis_system, 
									NEW.tanggal, NEW.pic_driver_masuk, 
									NEW.pic_driver_keluar, NEW.pic_no_pol_masuk, NEW.pic_no_pol_keluar, 
									NEW.sinkron, NEW.adm, NEW.alasan, NEW.pmlogin, NEW.pklogin, NEW.upload, NEW.manual, 
									NEW.veri_kode, NEW.veri_check, NEW.veri_adm, NEW.veri_date, NEW.denda, 
									NEW.extra_bayar, NEW.no_barcode, NEW.jenis_langganan, NEW.post_pay, NEW.reff_kode);
      ELSE
        IF (NEW.status_transaksi='0') and (NEW.bayar_keluar > 0) and (NEW.status_transaksi<>'32') THEN
          IF (NEW.bayar_keluar < CONFIG.limit_value) and (OLD.bayar_keluar=0 or OLD.bayar_keluar is null)  THEN
            CONFIG.real := CONFIG.real + NEW.bayar_keluar;
	    delete from parkir_transaksi where id= NEW.id and waktu_masuk= NEW.waktu_masuk;
	    SELECT INTO TINTERVAL (select (tarif.interval::text || ' MINUTES')::interval+'10 MINUTES' from tarif where id_mobil=NEW.id_kendaraan);
            IF ((((CONFIG.audit+NEW.bayar_keluar)/CONFIG.real)*100)<CONFIG.ratio) THEN
              CONFIG.audit := CONFIG.audit + NEW.bayar_keluar;
            insert into parkir_transaksi (id,no_pol, id_kendaraan, status, id_pintu_masuk,
	  						id_pintu_keluar, waktu_masuk, waktu_keluar, id_op_masuk,
	  						id_op_keluar, id_shift_masuk, id_shift_keluar, kategori,
	  						status_transaksi, bayar_masuk, bayar_keluar, jenis_system,
	  						tanggal, pic_driver_masuk,
	  						pic_driver_keluar, pic_no_pol_masuk, pic_no_pol_keluar,
	  						sinkron, adm, alasan, pmlogin, pklogin, upload, manual,
	  						veri_kode, veri_check, veri_adm, veri_date, denda,
	  						extra_bayar, no_barcode, jenis_langganan, post_pay, reff_kode)  
	  						values(NEW.id, NEW.no_pol, NEW.id_kendaraan,NEW.status, NEW.id_pintu_masuk, 
	  						NEW.id_pintu_keluar, NEW.waktu_masuk, NEW.waktu_keluar, NEW.id_op_masuk, 
	  						NEW.id_op_keluar, NEW.id_shift_masuk, NEW.id_shift_keluar, NEW.kategori, 
	  						NEW.status_transaksi, NEW.bayar_masuk, NEW.bayar_keluar, NEW.jenis_system, 
	  						NEW.tanggal, NEW.pic_driver_masuk, 
	  						NEW.pic_driver_keluar, NEW.pic_no_pol_masuk, NEW.pic_no_pol_keluar, 
	  						NEW.sinkron, NEW.adm, NEW.alasan, NEW.pmlogin, NEW.pklogin, NEW.upload, NEW.manual, 
	  						NEW.veri_kode, NEW.veri_check, NEW.veri_adm, NEW.veri_date, NEW.denda, 
	  						NEW.extra_bayar, NEW.no_barcode, NEW.jenis_langganan, NEW.post_pay, NEW.reff_kode);
              ELSE
     	      IF config.db='time.db' THEN
	         IF (age(NEW.waktu_keluar,NEW.waktu_masuk)>TINTERVAL) and (NEW.status_transaksi<>'32') THEN
		  	delete from parkir_transaksi where id= NEW.id and waktu_masuk= NEW.waktu_masuk;
			SELECT INTO POTONG (select tarif from tarif where id_mobil=NEW.id_kendaraan);
			SELECT INTO WAKTU_TARIF (select (tarif.waktu_tarif::text || ' MINUTES')::interval from tarif where id_mobil=NEW.id_kendaraan);
			SELECT INTO BAYAR (select (CASE WHEN bayar_masuk is null then 0 ELSE bayar_masuk END)+bayar_keluar from transaksi_parkir where id=NEW.id and no_pol=NEW.no_pol and waktu_masuk=NEW.waktu_masuk) - POTONG;
			SELECT INTO MASUK (select waktu_masuk from transaksi_parkir where id=NEW.id and no_pol=NEW.no_pol and waktu_masuk=NEW.waktu_masuk) + WAKTU_TARIF;
			CONFIG.audit := CONFIG.audit + BAYAR;
			insert into parkir_transaksi (id,no_pol, id_kendaraan, status, id_pintu_masuk,
							id_pintu_keluar, waktu_masuk, waktu_keluar, id_op_masuk,
							id_op_keluar, id_shift_masuk, id_shift_keluar, kategori,
							status_transaksi, bayar_masuk, bayar_keluar, jenis_system,
							tanggal, pic_driver_masuk,
							pic_driver_keluar, pic_no_pol_masuk, pic_no_pol_keluar,
							sinkron, adm, alasan, pmlogin, pklogin, upload, manual,
							veri_kode, veri_check, veri_adm, veri_date, denda,
							extra_bayar, no_barcode, jenis_langganan, post_pay, reff_kode)  
							values(NEW.id, NEW.no_pol, NEW.id_kendaraan, NEW.status, NEW.id_pintu_masuk, 
							NEW.id_pintu_keluar, MASUK, NEW.waktu_keluar, NEW.id_op_masuk, 
							NEW.id_op_keluar, NEW.id_shift_masuk, NEW.id_shift_keluar, NEW.kategori, 
							NEW.status_transaksi, NEW.bayar_masuk, BAYAR, NEW.jenis_system, 
							NEW.tanggal, NEW.pic_driver_masuk, 
							NEW.pic_driver_keluar, NEW.pic_no_pol_masuk, NEW.pic_no_pol_keluar, 
							NEW.sinkron, NEW.adm, NEW.alasan, NEW.pmlogin, NEW.pklogin, NEW.upload, NEW.manual, 
							NEW.veri_kode, NEW.veri_check, NEW.veri_adm, NEW.veri_date, NEW.denda, 
							NEW.extra_bayar, NEW.no_barcode, NEW.jenis_langganan, NEW.post_pay, NEW.reff_kode);

	         ELSE 
	          IF  (NEW.status_transaksi<>'32') THEN 
	           IF (NEW.bayar_keluar > 0) and (NEW.bayar_keluar < CONFIG.limit_value)  THEN
		  	CONFIG.audit := CONFIG.audit + NEW.bayar_keluar;
		   END IF;
		 
	           delete from parkir_transaksi where id= NEW.id and waktu_masuk= NEW.waktu_masuk;
                   insert into parkir_transaksi (id,no_pol, id_kendaraan, status, id_pintu_masuk,
							id_pintu_keluar, waktu_masuk, waktu_keluar, id_op_masuk,
							id_op_keluar, id_shift_masuk, id_shift_keluar, kategori,
							status_transaksi, bayar_masuk, bayar_keluar, jenis_system,
							tanggal, pic_driver_masuk,
							pic_driver_keluar, pic_no_pol_masuk, pic_no_pol_keluar,
							sinkron, adm, alasan, pmlogin, pklogin, upload, manual,
							veri_kode, veri_check, veri_adm, veri_date, denda,
							extra_bayar, no_barcode, jenis_langganan, post_pay, reff_kode)  
							values(NEW.id, NEW.no_pol, NEW.id_kendaraan,NEW.status, NEW.id_pintu_masuk, 
							NEW.id_pintu_keluar, NEW.waktu_masuk, NEW.waktu_keluar, NEW.id_op_masuk, 
							NEW.id_op_keluar, NEW.id_shift_masuk, NEW.id_shift_keluar, NEW.kategori, 
							NEW.status_transaksi, NEW.bayar_masuk, NEW.bayar_keluar, NEW.jenis_system, 
							NEW.tanggal, NEW.pic_driver_masuk, 
							NEW.pic_driver_keluar, NEW.pic_no_pol_masuk, NEW.pic_no_pol_keluar, 
							NEW.sinkron, NEW.adm, NEW.alasan, NEW.pmlogin, NEW.pklogin, NEW.upload, NEW.manual, 
							NEW.veri_kode, NEW.veri_check, NEW.veri_adm, NEW.veri_date, NEW.denda, 
							NEW.extra_bayar, NEW.no_barcode, NEW.jenis_langganan, NEW.post_pay, NEW.reff_kode);
		  END IF;
                 END IF;
              ELSE
                IF config.db='empty.db' THEN
	          insert into parkir_transaksi (id,no_pol, id_kendaraan, status, id_pintu_masuk,
							id_pintu_keluar, waktu_masuk, waktu_keluar, id_op_masuk,
							id_op_keluar, id_shift_masuk, id_shift_keluar, kategori,
							status_transaksi, bayar_masuk, bayar_keluar, jenis_system,
							tanggal, pic_driver_masuk,
							pic_driver_keluar, pic_no_pol_masuk, pic_no_pol_keluar,
							sinkron, adm, alasan, pmlogin, pklogin, upload, manual,
							veri_kode, veri_check, veri_adm, veri_date, denda,
							extra_bayar, no_barcode, jenis_langganan, post_pay, reff_kode)  
							values(NEW.id, NEW.no_pol, NEW.id_kendaraan,NEW.status, NEW.id_pintu_masuk, 
							NEW.id_pintu_keluar, NEW.waktu_masuk, NEW.waktu_keluar, NEW.id_op_masuk, 
							NEW.id_op_keluar, NEW.id_shift_masuk, NEW.id_shift_keluar, NEW.kategori, 
							NEW.status_transaksi, 0, 0, NEW.jenis_system, 
							NEW.tanggal, NEW.pic_driver_masuk, 
							NEW.pic_driver_keluar, NEW.pic_no_pol_masuk, NEW.pic_no_pol_keluar, 
							NEW.sinkron, NEW.adm, NEW.alasan, NEW.pmlogin, NEW.pklogin, NEW.upload, NEW.manual, 
							'0123456789', 1, '0001', NEW.veri_date, NEW.denda, 
							NEW.extra_bayar, NEW.no_barcode, NEW.jenis_langganan, NEW.post_pay, NEW.reff_kode);
	         ELSE
	         END IF;
               END IF;
            END IF;
          END IF; 
        ELSE
          IF (NEW.status_transaksi='-1')  THEN
            UPDATE parkir_transaksi set status_transaksi='-1' where id=NEW.id and no_pol=NEW.no_pol and waktu_keluar=NEW.waktu_keluar;
          ELSE
            IF (NEW.status_transaksi<>'32') THEN 
       	      delete from parkir_transaksi where id= NEW.id and waktu_masuk= NEW.waktu_masuk;
              insert into parkir_transaksi (  id,no_pol, id_kendaraan, status, id_pintu_masuk,
									id_pintu_keluar, waktu_masuk, waktu_keluar, id_op_masuk,
									id_op_keluar, id_shift_masuk, id_shift_keluar, kategori,
									status_transaksi, bayar_masuk, bayar_keluar, jenis_system,
									tanggal, pic_driver_masuk,
									pic_driver_keluar, pic_no_pol_masuk, pic_no_pol_keluar,
									sinkron, adm, alasan, pmlogin, pklogin, upload, manual,
									veri_kode, veri_check, veri_adm, veri_date, denda,
									extra_bayar, no_barcode, jenis_langganan, post_pay, reff_kode)  
									values( 
									NEW.id, NEW.no_pol, NEW.id_kendaraan, NEW.status, NEW.id_pintu_masuk, 
									NEW.id_pintu_keluar, NEW.waktu_masuk, NEW.waktu_keluar, NEW.id_op_masuk, 
									NEW.id_op_keluar, NEW.id_shift_masuk, NEW.id_shift_keluar, NEW.kategori, 
									NEW.status_transaksi, NEW.bayar_masuk, NEW.bayar_keluar, NEW.jenis_system, 
									NEW.tanggal, NEW.pic_driver_masuk, 
									NEW.pic_driver_keluar, NEW.pic_no_pol_masuk, NEW.pic_no_pol_keluar, 
									NEW.sinkron, NEW.adm, NEW.alasan, NEW.pmlogin, NEW.pklogin, NEW.upload, NEW.manual, 
									NEW.veri_kode, NEW.veri_check, NEW.veri_adm, NEW.veri_date, NEW.denda, 
									NEW.extra_bayar, NEW.no_barcode, NEW.jenis_langganan, NEW.post_pay, NEW.reff_kode);
             END IF;
            END IF;
        END IF;
      END IF;
    END IF;
    
    IF (TG_OP='DELETE') THEN
      IF (OLD.bayar_keluar > 0) and (OLD.status = 0) and (OLD.bayar_keluar < CONFIG.limit_value)  THEN
        CONFIG.real := CONFIG.real - OLD.bayar_keluar;     
        CONFIG.audit := CONFIG.audit - OLD.bayar_keluar;     
      END IF;
      delete from parkir_transaksi where id= OLD.id and no_pol= OLD.no_pol and waktu_masuk= OLD.waktu_masuk;
    END IF;

    IF CONFIG.real < 0 THEN
      CONFIG.real := 0;
    END IF;

    IF CONFIG.audit < 0 THEN
      CONFIG.audit := 0;
    END IF;

    UPDATE nx_audit SET real=CONFIG.real, audit=CONFIG.audit, last=now();
     
    RETURN NULL;
  END;  
$$;


--
-- TOC entry 248 (class 1255 OID 16398)
-- Dependencies: 856 6
-- Name: transaksi_parkir_cannot_delete(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION transaksi_parkir_cannot_delete() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ BEGIN if (TG_OP='DELETE') then INSERT INTO transaksi_parkir (id, no_pol, id_kendaraan, status, id_pintu_masuk, id_pintu_keluar, waktu_masuk, waktu_keluar, id_op_masuk, id_op_keluar, id_shift_masuk, id_shift_keluar, kategori, status_transaksi, bayar_masuk, bayar_keluar, jenis_system, tanggal, sinkron, adm, alasan, pmlogin, pklogin, upload, manual, veri_kode, veri_check, veri_adm, veri_date, denda, extra_bayar, no_barcode) VALUES (OLD.id, OLD.no_pol, OLD.id_kendaraan, OLD.status, OLD.id_pintu_masuk, OLD.id_pintu_keluar, OLD.waktu_masuk, OLD.waktu_keluar, OLD.id_op_masuk, OLD.id_op_keluar, OLD.id_shift_masuk, OLD.id_shift_keluar, OLD.kategori, OLD.status_transaksi, OLD.bayar_masuk, OLD.bayar_keluar, OLD.jenis_system, OLD.tanggal, OLD.sinkron, OLD.adm, OLD.alasan, OLD.pmlogin, OLD.pklogin, OLD.upload, OLD.manual, OLD.veri_kode, OLD.veri_check, OLD.veri_adm, OLD.veri_date, OLD.denda, OLD.extra_bayar, OLD.no_barcode); END IF; return OLD; END $$;


SET default_tablespace = '';

SET default_with_oids = true;

--
-- TOC entry 140 (class 1259 OID 16399)
-- Dependencies: 6
-- Name: agama; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE agama (
    kode character varying(50),
    nama character varying(50)
);


--
-- TOC entry 141 (class 1259 OID 16402)
-- Dependencies: 6
-- Name: aksespegawai; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE aksespegawai (
    form integer NOT NULL,
    password character varying(50) NOT NULL,
    status smallint NOT NULL,
    idcard character varying(50)
);


--
-- TOC entry 142 (class 1259 OID 16405)
-- Dependencies: 6
-- Name: aksestable; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE aksestable (
    idcard character varying(50),
    idform integer
);


--
-- TOC entry 2381 (class 0 OID 0)
-- Dependencies: 142
-- Name: TABLE aksestable; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE aksestable IS 'tabel akses untuk setiap form';


--
-- TOC entry 143 (class 1259 OID 16408)
-- Dependencies: 6
-- Name: biaya_admin; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE biaya_admin (
    kode character varying(5),
    nilai real,
    jenis_kendaraan character varying(10),
    keterangan character varying(100),
    nilai_poin integer
);


--
-- TOC entry 144 (class 1259 OID 16411)
-- Dependencies: 6
-- Name: biaya_poin; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE biaya_poin (
    kode character varying(5),
    nilai real,
    nilai_poin real,
    jenis_kendaraan character varying(10),
    keterangan character varying(50),
    masa_aktif smallint
);


SET default_with_oids = false;

--
-- TOC entry 145 (class 1259 OID 16414)
-- Dependencies: 6
-- Name: blacklist_kendaraan; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE blacklist_kendaraan (
    no_pol character varying(30),
    alasan character varying,
    tanggal timestamp without time zone,
    level integer,
    status integer
);


--
-- TOC entry 146 (class 1259 OID 16420)
-- Dependencies: 6
-- Name: card_member; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE card_member (
    notrans character varying,
    no_card character varying,
    no_urut character varying,
    tanggal timestamp without time zone,
    adm character varying
);


--
-- TOC entry 147 (class 1259 OID 16426)
-- Dependencies: 6
-- Name: card_member_rest; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE card_member_rest (
    notrans character varying,
    no_card character varying,
    no_urut character varying,
    alasan character varying,
    tanggal timestamp without time zone,
    adm character varying
);


--
-- TOC entry 148 (class 1259 OID 16432)
-- Dependencies: 6
-- Name: clevel_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE clevel_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2382 (class 0 OID 0)
-- Dependencies: 148
-- Name: clevel_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('clevel_seq', 4, true);


--
-- TOC entry 149 (class 1259 OID 16434)
-- Dependencies: 6
-- Name: config_file; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE config_file (
    exit_pass smallint,
    jam_malam_mulai character varying,
    jam_malam_selesai character varying,
    pengguna_exit_pass smallint,
    footer_in_1 character varying,
    footer_in_3 character varying,
    footer_in_2 character varying,
    footer_out_1 character varying,
    footer_out_2 character varying,
    footer_out_3 character varying,
    cetak_tambahan_in character varying(1024),
    cetak_tambahan_out character varying(1024)
);


SET default_with_oids = true;

--
-- TOC entry 150 (class 1259 OID 16440)
-- Dependencies: 2198 2199 2200 2201 2202 2203 2204 2205 2206 2207 2208 6
-- Name: config_pos; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE config_pos (
    prefix character varying(3),
    max_load_index integer,
    camera_refresh integer,
    max_nopol_avail integer,
    max_nopol integer,
    max_member_on_a_time integer,
    message integer,
    info_member integer,
    ploting integer,
    info_volume integer,
    login_a_time integer,
    tiket_masalah integer,
    use_barcode integer,
    warning_member integer,
    start_warning_member integer,
    add_barcode_struk_in integer,
    type_barcode_struk_in integer,
    input_kode_pisah integer,
    cek_mobil_masalah integer,
    overwrite integer,
    no_reinput integer,
    pos_for_any_kode integer,
    any_kode character varying(1),
    confirm_input integer,
    akses_for_reprint integer,
    no_input_notrans integer,
    only_input_any_digit integer,
    any_digit integer,
    input_notrans_only_open_gate integer,
    max_input_notrans integer,
    max_input_notrans_value integer,
    autoprint_struk integer,
    reprint_struk_activ integer,
    no_reinput_out integer,
    id_pos character varying(5),
    shortcut_kode character varying(2),
    footer1 character varying,
    footer2 character varying,
    cetak_tambahan character varying,
    ouc integer,
    ouc_tipe_barcode integer,
    footer3 character varying,
    footer4 character varying,
    kend_valid character varying,
    swapable smallint,
    id_pos_alternative character varying(5),
    manual_bg_enable integer DEFAULT 1,
    disable_manual integer,
    enable_icmp integer,
    show_print_counter integer,
    detail_muatan integer DEFAULT 0,
    soe integer DEFAULT 0,
    lbi integer DEFAULT 0,
    falidasi_instant integer DEFAULT 0,
    print_total_nol integer DEFAULT 0,
    iuc integer DEFAULT 0,
    vericode_unix integer DEFAULT 1,
    limit_validasi integer DEFAULT 1,
    form_denda integer DEFAULT 0,
    customer_counter integer DEFAULT 0,
    debug_window integer,
    aktivasi_voucher integer,
    interval_time_member integer,
    min_interval_time_member integer
);


--
-- TOC entry 151 (class 1259 OID 16457)
-- Dependencies: 6
-- Name: config_pos_hardware; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE config_pos_hardware (
    printer1_avail integer,
    printer1_conn character varying(20),
    printer1_spd character varying(6),
    printer1_stdfile integer,
    printer1_autocutter integer,
    printer1_bgconnect integer,
    printer1_dummy integer,
    video1_avail integer,
    video1_conn character varying(200),
    video1_channel integer,
    video1_version integer,
    feedisplay_avail integer,
    feedisplay_conn character varying(20),
    feedisplay_paralel character varying(6),
    feedisplay_version integer,
    bg_avail integer,
    bg_conn character varying(20),
    bg_paralel integer,
    bg_value integer,
    sound_avail integer,
    sound_conn character varying(20),
    sound_version integer,
    sound_partisi integer,
    id_pos character varying(5),
    sizeable integer,
    pjg_lcd integer,
    video1_bright character varying,
    video2_avail integer,
    video2_conn character varying(200),
    video2_channel integer,
    video2_version integer,
    video2_bright character varying,
    video2_sizeable integer,
    smartcard_avail smallint,
    smartcard_speed integer,
    smartcard_port character varying(32),
    printer2_avail integer,
    printer2_conn character varying(20),
    printer2_spd character varying(6),
    printer2_stdfile integer,
    printer2_autocutter integer,
    printer2_bgconnect integer,
    printer2_dummy integer,
    fan1_maxval integer,
    fan2_maxval integer,
    temp1_maxval integer,
    temp2_maxval integer,
    sensor_fan1 integer,
    sensor_fan2 integer,
    sensor_temp1 integer,
    sensor_temp2 integer,
    bg_type integer,
    bg_usb integer,
    video3_avail integer,
    video3_conn character varying(200),
    video3_channel integer,
    video3_version integer,
    video3_bright character varying,
    video3_sizeable integer
);


--
-- TOC entry 152 (class 1259 OID 16463)
-- Dependencies: 2209 6
-- Name: customer; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE customer (
    kode character varying(20),
    nama character varying(50),
    alamat character varying(300),
    telepon character varying(20),
    fax character varying(20),
    email character varying(50),
    cp character varying(50),
    telpcp character varying(20),
    status smallint,
    konfirmasi character varying(50),
    approved character varying(30),
    member smallint DEFAULT 0,
    adm character varying(20)
);


--
-- TOC entry 153 (class 1259 OID 16470)
-- Dependencies: 6
-- Name: detail_customer; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE detail_customer (
    kode character varying(20),
    idcust character varying(20),
    nopol character varying(20),
    nosticker character varying(10),
    status smallint,
    stokpulsa integer,
    jenis_kendaraan character varying(3),
    ktp character varying(50),
    tgltrans timestamp without time zone,
    masa_aktif timestamp without time zone,
    tglaktif timestamp without time zone,
    alamat character varying,
    telepon character varying(25)
);


--
-- TOC entry 154 (class 1259 OID 16476)
-- Dependencies: 2210 6
-- Name: detail_langganan; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE detail_langganan (
    id_langganan character varying(50) NOT NULL,
    nopol character varying(50) NOT NULL,
    jenis character varying(50),
    akses character varying(50),
    enable smallint DEFAULT 1
);


--
-- TOC entry 155 (class 1259 OID 16480)
-- Dependencies: 2211 6
-- Name: detail_langganan_next; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE detail_langganan_next (
    id_langganan character varying(50) NOT NULL,
    nopol character varying(50) NOT NULL,
    jenis character varying(50),
    akses character varying(50),
    enable smallint DEFAULT 1
);


--
-- TOC entry 156 (class 1259 OID 16484)
-- Dependencies: 6
-- Name: detail_pendaftaran; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE detail_pendaftaran (
    notrans character varying(20),
    idcard character varying(20),
    nilai real,
    jenis_kendaraan character varying(3),
    nopol character varying(30)
);


--
-- TOC entry 157 (class 1259 OID 16487)
-- Dependencies: 6
-- Name: detail_transaksi_parkir; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE detail_transaksi_parkir (
    notrans character varying(20),
    tgl timestamp without time zone,
    jenis_kendaraan character varying(3),
    nopol character varying(20),
    jml smallint,
    total real,
    status smallint,
    waktu_masuk timestamp without time zone
);


--
-- TOC entry 158 (class 1259 OID 16490)
-- Dependencies: 6
-- Name: detail_transaksi_pulsa; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE detail_transaksi_pulsa (
    notrans character varying(20),
    harga double precision,
    point double precision,
    idcard character varying(20),
    tglaktivasi timestamp without time zone,
    status smallint,
    masa_aktif smallint,
    jenis_kendaraan character varying(3),
    nopol character varying(30),
    adm character varying(60),
    discount double precision
);


--
-- TOC entry 159 (class 1259 OID 16493)
-- Dependencies: 2212 6
-- Name: detail_transaksi_stiker; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE detail_transaksi_stiker (
    notrans character varying(50),
    nopol character varying(50),
    jenis_mobil character varying(50),
    adm character varying(10),
    kategori smallint,
    jenis_member character varying,
    akses character varying,
    akses_out character varying,
    status integer DEFAULT 1,
    merk character varying,
    tipe character varying,
    tahun character varying,
    warna character varying,
    keterangan character varying(255)
);


--
-- TOC entry 160 (class 1259 OID 16500)
-- Dependencies: 6
-- Name: detailpolajamkerja; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE detailpolajamkerja (
    hari smallint NOT NULL,
    masuk timestamp without time zone NOT NULL,
    lama double precision NOT NULL,
    efektif smallint NOT NULL,
    keterangan character varying(255),
    idpola character varying(50),
    imasuk timestamp without time zone,
    ilama double precision
);


--
-- TOC entry 161 (class 1259 OID 16503)
-- Dependencies: 6
-- Name: fingerlist; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE fingerlist (
    idcard character varying(50),
    idfinger smallint,
    finger bytea
);


--
-- TOC entry 2383 (class 0 OID 0)
-- Dependencies: 161
-- Name: TABLE fingerlist; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE fingerlist IS 'data finger di simpan untuk semua langganan';


SET default_with_oids = false;

--
-- TOC entry 162 (class 1259 OID 16509)
-- Dependencies: 6
-- Name: foc; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE foc (
    notrans character varying,
    id_langganan character varying,
    nama character varying,
    tanggal character varying
);


SET default_with_oids = true;

--
-- TOC entry 163 (class 1259 OID 16515)
-- Dependencies: 6
-- Name: freepass; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE freepass (
    nomer character varying(50) NOT NULL,
    tanggal timestamp without time zone NOT NULL,
    tgl_enable timestamp without time zone,
    nopol character varying(50),
    jenis_mobil character varying(50),
    petugas character varying(50),
    id_pos character varying(50),
    id_shift character varying(50),
    enable smallint,
    seri character varying(10),
    pklogin timestamp without time zone,
    tgl_trans timestamp without time zone,
    nama character varying,
    aktif integer,
    input integer
);


--
-- TOC entry 164 (class 1259 OID 16521)
-- Dependencies: 6
-- Name: freepass_activation_log; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE freepass_activation_log (
    nomer character varying(50) NOT NULL,
    tanggal timestamp without time zone NOT NULL,
    tgl_enable timestamp without time zone,
    nopol character varying(50),
    jenis_mobil character varying(50),
    petugas character varying(50),
    id_pos character varying(50),
    id_shift character varying(50),
    enable smallint
);


--
-- TOC entry 165 (class 1259 OID 16524)
-- Dependencies: 6
-- Name: hari_libur; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE hari_libur (
    tanggal timestamp without time zone NOT NULL,
    keterangan character varying(255)
);


--
-- TOC entry 166 (class 1259 OID 16527)
-- Dependencies: 2213 6
-- Name: indexnum; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE indexnum (
    kode character varying(20) NOT NULL,
    nama character varying(255) NOT NULL,
    value character varying(50) DEFAULT '0'::character varying
);


--
-- TOC entry 167 (class 1259 OID 16531)
-- Dependencies: 6
-- Name: jenis_langganan; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE jenis_langganan (
    id character varying(10),
    nama character varying(50),
    bayar smallint,
    tarif integer,
    periode_awal timestamp without time zone,
    masa_berlaku integer,
    maks integer,
    jenis_mobil character varying
);


--
-- TOC entry 2384 (class 0 OID 0)
-- Dependencies: 167
-- Name: COLUMN jenis_langganan.masa_berlaku; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN jenis_langganan.masa_berlaku IS 'Satuan dalam bulan';


--
-- TOC entry 168 (class 1259 OID 16537)
-- Dependencies: 2214 2215 6
-- Name: jenis_mobil; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE jenis_mobil (
    id character varying(20) NOT NULL,
    nama character varying(50) NOT NULL,
    tanggal timestamp without time zone NOT NULL,
    short_cut character varying(10),
    orang smallint DEFAULT 0,
    validasi smallint,
    need_access integer DEFAULT 0
);


SET default_with_oids = false;

--
-- TOC entry 169 (class 1259 OID 16542)
-- Dependencies: 6
-- Name: keyallow; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE keyallow (
    idkey character varying,
    keycode character varying,
    reg_date character varying
);


SET default_with_oids = true;

--
-- TOC entry 170 (class 1259 OID 16548)
-- Dependencies: 6
-- Name: kodeform; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE kodeform (
    kode integer NOT NULL,
    nama character varying(100)
);


--
-- TOC entry 2385 (class 0 OID 0)
-- Dependencies: 170
-- Name: TABLE kodeform; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE kodeform IS 'kode untuk setiap form yang berada di aplikasi';


--
-- TOC entry 171 (class 1259 OID 16551)
-- Dependencies: 6
-- Name: konsolidasi; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE konsolidasi (
    notrans character varying(50),
    nopol character varying(50),
    jam_masuk timestamp without time zone,
    status_transaksi character varying(20),
    status character varying(20),
    user_id character varying(20),
    tgl_kons timestamp without time zone,
    bayar double precision
);


--
-- TOC entry 172 (class 1259 OID 16554)
-- Dependencies: 2216 6
-- Name: kredit; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE kredit (
    notrans character varying(15),
    jenis character varying(10),
    tgl timestamp without time zone,
    pemilik character varying(50),
    nomer character varying(30),
    total double precision,
    status smallint DEFAULT 0
);


--
-- TOC entry 173 (class 1259 OID 16558)
-- Dependencies: 2217 2218 6
-- Name: langganan; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE langganan (
    id character varying(50) NOT NULL,
    nama character varying(255) NOT NULL,
    alamat character varying(255),
    telepon character varying(50),
    enable smallint DEFAULT 1,
    tanggal timestamp without time zone,
    keyid character varying(255),
    jenis_langganan smallint,
    awal timestamp without time zone,
    akhir timestamp without time zone,
    no_induk character varying(25),
    max smallint DEFAULT 1,
    unit_kerja character varying(20),
    adm character varying(50),
    area character varying(255)
);


--
-- TOC entry 2386 (class 0 OID 0)
-- Dependencies: 173
-- Name: TABLE langganan; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE langganan IS 'jenis_langganan -> 0 = permanent
                               1 = Temporary';


--
-- TOC entry 2387 (class 0 OID 0)
-- Dependencies: 173
-- Name: COLUMN langganan.jenis_langganan; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN langganan.jenis_langganan IS '0/null = permanent
1        = terbatas gratis
2        = stiker';


--
-- TOC entry 174 (class 1259 OID 16566)
-- Dependencies: 2219 2220 6
-- Name: langganan_next; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE langganan_next (
    id character varying(50) NOT NULL,
    nama character varying(255) NOT NULL,
    alamat character varying(255),
    telepon character varying(50),
    enable smallint DEFAULT 1,
    tanggal timestamp without time zone,
    keyid character varying(255),
    jenis_langganan smallint,
    awal timestamp without time zone,
    akhir timestamp without time zone,
    no_induk character varying(25),
    max smallint DEFAULT 1,
    unit_kerja character varying(20),
    adm character varying(50)
);


--
-- TOC entry 175 (class 1259 OID 16574)
-- Dependencies: 2221 2222 6
-- Name: langganan_res; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE langganan_res (
    id character varying(50) NOT NULL,
    nama character varying(255) NOT NULL,
    alamat character varying(255),
    telepon character varying(50),
    enable smallint DEFAULT 1,
    tanggal timestamp without time zone,
    keyid character varying(255),
    jenis_langganan smallint,
    awal timestamp without time zone,
    akhir timestamp without time zone,
    no_induk character varying(25),
    max smallint DEFAULT 1,
    unit_kerja character varying(20),
    adm character varying(50),
    nopol character varying(50) NOT NULL,
    jenis character varying(50),
    akses character varying(50),
    enable_detail character varying
);


--
-- TOC entry 176 (class 1259 OID 16582)
-- Dependencies: 2223 6
-- Name: level_user; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE level_user (
    level_id integer DEFAULT nextval('clevel_seq'::regclass) NOT NULL,
    level_code character varying(10) NOT NULL,
    level_name character varying(30),
    create_by character varying NOT NULL,
    create_date timestamp without time zone,
    update_by integer,
    update_date timestamp without time zone
);


--
-- TOC entry 177 (class 1259 OID 16589)
-- Dependencies: 6
-- Name: login_log; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE login_log (
    id_petugas character varying(20) NOT NULL,
    id_shift character varying(20) NOT NULL,
    time_login timestamp without time zone NOT NULL,
    time_logout timestamp without time zone,
    tanggal timestamp without time zone NOT NULL,
    pos character varying(10),
    akses_id character varying(64),
    adm character varying(16)
);


SET default_with_oids = false;

--
-- TOC entry 178 (class 1259 OID 16592)
-- Dependencies: 6
-- Name: lot_parkir; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE lot_parkir (
    lot character varying(16),
    id_lokasi character varying(5) NOT NULL,
    used smallint NOT NULL
);


SET default_with_oids = true;

--
-- TOC entry 179 (class 1259 OID 16595)
-- Dependencies: 6
-- Name: manualbot; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE manualbot (
    petugas character varying(20) NOT NULL,
    id_shift character varying(20) NOT NULL,
    id_pos character varying(20) NOT NULL,
    tanggal timestamp without time zone NOT NULL,
    pic bytea
);


--
-- TOC entry 180 (class 1259 OID 16601)
-- Dependencies: 6
-- Name: master_device; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE master_device (
    id_device character varying(20),
    nama_device character varying(30),
    tipe smallint,
    kat smallint,
    id_lokasi character varying(20),
    pesan character varying(255),
    refresh smallint,
    id_lokasi_join character varying(20)
);


--
-- TOC entry 181 (class 1259 OID 16604)
-- Dependencies: 6
-- Name: master_lokasi; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE master_lokasi (
    id_lokasi character varying(20),
    nama_lokasi character varying(30),
    max_space smallint,
    sisa smallint,
    prioritas integer
);


--
-- TOC entry 182 (class 1259 OID 16607)
-- Dependencies: 6
-- Name: menuavail; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE menuavail (
    kode character varying(50) NOT NULL,
    keterangan character varying(255) NOT NULL
);


--
-- TOC entry 183 (class 1259 OID 16610)
-- Dependencies: 1996 6
-- Name: mergelangganandandetail; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW mergelangganandandetail AS
    SELECT langganan.id, langganan.nama, langganan.alamat, langganan.telepon, langganan.enable, langganan.tanggal, langganan.keyid, langganan.jenis_langganan, langganan.awal, langganan.akhir, langganan.no_induk, langganan.max, langganan.unit_kerja, langganan.adm, detail_langganan.nopol, detail_langganan.jenis, detail_langganan.akses, detail_langganan.enable AS enable_detail FROM (langganan LEFT JOIN detail_langganan ON (((langganan.id)::text = (detail_langganan.id_langganan)::text)));


--
-- TOC entry 184 (class 1259 OID 16614)
-- Dependencies: 1997 6
-- Name: mergelangganandandetail_next; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW mergelangganandandetail_next AS
    SELECT langganan_next.id, langganan_next.nama, langganan_next.alamat, langganan_next.telepon, langganan_next.enable, langganan_next.tanggal, langganan_next.keyid, langganan_next.jenis_langganan, langganan_next.awal, langganan_next.akhir, langganan_next.no_induk, langganan_next.max, langganan_next.unit_kerja, langganan_next.adm, detail_langganan_next.nopol, detail_langganan_next.jenis, detail_langganan_next.akses, detail_langganan_next.enable AS enable_detail FROM (langganan_next LEFT JOIN detail_langganan_next ON (((langganan_next.id)::text = (detail_langganan_next.id_langganan)::text)));


SET default_with_oids = false;

--
-- TOC entry 185 (class 1259 OID 16618)
-- Dependencies: 2224 2225 2226 2227 6
-- Name: transaksi_stiker; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE transaksi_stiker (
    notrans character varying(50) NOT NULL,
    alamat character varying(50),
    telepon character varying(50),
    jenis_transaksi smallint,
    awal timestamp without time zone,
    harga double precision,
    keterangan character varying(255),
    tanggal timestamp without time zone,
    operator character varying(50),
    akhir timestamp without time zone,
    maks smallint DEFAULT 1,
    no_id character varying(50),
    unit_kerja character varying(20),
    no_induk character varying(25),
    jenis_stiker smallint,
    hari_ke character varying,
    jenis_langganan character varying,
    exit_pass smallint,
    no_kuitansi character varying,
    tgl_edited timestamp without time zone,
    tipe_exit_pass integer DEFAULT 0,
    seq_code character varying(10),
    unitno character varying(10),
    area character varying(255),
    batasan_jam integer DEFAULT 0,
    batasan_awal character varying(16),
    batasan_akhir character varying(16),
    reserved integer DEFAULT 0,
    nama character varying(100),
    max_free_any_time integer,
    start_time_max_free character varying(10),
    stop_time_max_free character varying(10),
    biaya_langganan integer,
    biaya_parkir integer,
    batasan_for_weekday integer,
    disabled integer
);


--
-- TOC entry 186 (class 1259 OID 16628)
-- Dependencies: 1998 6
-- Name: mergetransaksistikerdetail; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW mergetransaksistikerdetail AS
    SELECT transaksi_stiker.notrans, transaksi_stiker.jenis_transaksi, transaksi_stiker.jenis_langganan, transaksi_stiker.awal AS periode, transaksi_stiker.harga, transaksi_stiker.keterangan, transaksi_stiker.tanggal, transaksi_stiker.operator, transaksi_stiker.nama, transaksi_stiker.awal, transaksi_stiker.akhir, transaksi_stiker.alamat, transaksi_stiker.tgl_edited, transaksi_stiker.telepon, transaksi_stiker.no_id, transaksi_stiker.maks, transaksi_stiker.unit_kerja, transaksi_stiker.jenis_stiker, transaksi_stiker.hari_ke, transaksi_stiker.exit_pass, transaksi_stiker.tipe_exit_pass, transaksi_stiker.seq_code, transaksi_stiker.unitno, transaksi_stiker.area, transaksi_stiker.reserved, transaksi_stiker.batasan_jam, transaksi_stiker.batasan_awal, transaksi_stiker.batasan_for_weekday, transaksi_stiker.max_free_any_time, transaksi_stiker.start_time_max_free, transaksi_stiker.stop_time_max_free, transaksi_stiker.batasan_akhir, transaksi_stiker.no_kuitansi, detail_transaksi_stiker.nopol, detail_transaksi_stiker.jenis_mobil, detail_transaksi_stiker.jenis_member, detail_transaksi_stiker.akses, detail_transaksi_stiker.akses_out, detail_transaksi_stiker.status FROM (transaksi_stiker LEFT JOIN detail_transaksi_stiker ON (((detail_transaksi_stiker.notrans)::text = (transaksi_stiker.notrans)::text))) ORDER BY detail_transaksi_stiker.nopol, transaksi_stiker.tgl_edited;


SET default_with_oids = true;

--
-- TOC entry 187 (class 1259 OID 16633)
-- Dependencies: 2228 6
-- Name: nama_pos; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE nama_pos (
    id character varying(20) NOT NULL,
    nama character varying(50) NOT NULL,
    jenis smallint NOT NULL,
    tanggal timestamp without time zone NOT NULL,
    lokasi character varying(20),
    grace_period smallint DEFAULT 1,
    manless integer,
    area character varying(10),
    berlaku_maksimal integer
);


--
-- TOC entry 2388 (class 0 OID 0)
-- Dependencies: 187
-- Name: TABLE nama_pos; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE nama_pos IS 'jenis 0 = masuk
        1 = keluar';


--
-- TOC entry 188 (class 1259 OID 16637)
-- Dependencies: 6
-- Name: netlist; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE netlist (
    ip character varying(50) NOT NULL,
    nama character varying(50),
    enable smallint NOT NULL,
    jenis smallint NOT NULL
);


--
-- TOC entry 189 (class 1259 OID 16640)
-- Dependencies: 6
-- Name: nodestatus; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE nodestatus (
    ip character varying(50) NOT NULL,
    id_node character varying(50),
    id_petugas character varying(50),
    event character varying(255),
    temp0 real,
    temp1 real,
    rpm0 real,
    rpm1 real,
    tanggal timestamp without time zone
);


--
-- TOC entry 190 (class 1259 OID 16643)
-- Dependencies: 6
-- Name: nopolpool; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE nopolpool (
    nopol character varying(50) NOT NULL,
    status smallint NOT NULL
);


--
-- TOC entry 191 (class 1259 OID 16646)
-- Dependencies: 2229 2230 2231 6
-- Name: nx_audit; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE nx_audit (
    db character varying(64) NOT NULL,
    ratio smallint NOT NULL,
    "real" integer DEFAULT 0,
    audit integer DEFAULT 0,
    last timestamp without time zone DEFAULT now(),
    awal integer,
    akhir integer,
    limit_value double precision
);


--
-- TOC entry 192 (class 1259 OID 16652)
-- Dependencies: 2232 2233 2234 2235 2236 2237 2238 6
-- Name: transaksi_parkir; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE transaksi_parkir (
    id character varying(20) NOT NULL,
    no_pol character varying(20) NOT NULL,
    id_kendaraan character varying(20) NOT NULL,
    status smallint NOT NULL,
    id_pintu_masuk character varying(20),
    id_pintu_keluar character varying(20),
    waktu_masuk timestamp without time zone,
    waktu_keluar timestamp without time zone,
    id_op_masuk character varying(20),
    id_op_keluar character varying(20),
    id_shift_masuk character varying(20),
    id_shift_keluar character varying(20),
    kategori character varying(20),
    status_transaksi character varying(20),
    bayar_masuk double precision DEFAULT 0,
    bayar_keluar double precision DEFAULT 0,
    jenis_system character varying(20),
    tanggal timestamp without time zone NOT NULL,
    pic_body_masuk bytea,
    pic_body_keluar bytea,
    pic_driver_masuk bytea,
    pic_driver_keluar bytea,
    pic_no_pol_masuk bytea,
    pic_no_pol_keluar bytea,
    sinkron smallint DEFAULT 0,
    adm character varying(10),
    alasan character varying(200),
    pmlogin timestamp without time zone,
    pklogin timestamp without time zone,
    upload smallint DEFAULT 0,
    manual smallint DEFAULT 0,
    veri_kode character varying(100),
    veri_check smallint,
    veri_adm character varying(50),
    veri_date timestamp without time zone,
    denda double precision,
    extra_bayar double precision,
    no_barcode character varying(30),
    jenis_langganan character varying(20),
    post_pay integer,
    reff_kode character varying,
    valet_adm character varying,
    waktu_valet timestamp without time zone,
    valet_charge integer,
    valet_ops character varying(10),
    valet_nopol character varying(15),
    login_waktu_valet timestamp without time zone,
    cara_bayar integer,
    unit_member character varying(20),
    reserved integer DEFAULT 0,
    casual_denda integer DEFAULT 0,
    no_voucher character varying(32),
    seri_voucher character varying(16),
    no_access_in character varying(64),
    no_access_out character varying(64),
    inap integer,
    pic_plat_masuk bytea,
    pic_plat_keluar bytea
);


--
-- TOC entry 193 (class 1259 OID 16665)
-- Dependencies: 1999 6
-- Name: parkir_sbg; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW parkir_sbg AS
    SELECT transaksi_parkir.id, transaksi_parkir.no_pol, transaksi_parkir.id_kendaraan, transaksi_parkir.status, transaksi_parkir.id_pintu_masuk, transaksi_parkir.id_pintu_keluar, transaksi_parkir.waktu_masuk, transaksi_parkir.waktu_keluar, transaksi_parkir.id_op_masuk, transaksi_parkir.id_op_keluar, transaksi_parkir.id_shift_masuk, transaksi_parkir.id_shift_keluar, transaksi_parkir.kategori, transaksi_parkir.status_transaksi, transaksi_parkir.bayar_masuk, transaksi_parkir.bayar_keluar, transaksi_parkir.jenis_system, transaksi_parkir.tanggal, transaksi_parkir.pic_body_masuk, transaksi_parkir.pic_body_keluar, transaksi_parkir.pic_driver_masuk, transaksi_parkir.pic_driver_keluar, transaksi_parkir.pic_no_pol_masuk, transaksi_parkir.pic_no_pol_keluar FROM transaksi_parkir WHERE (transaksi_parkir.waktu_masuk > (((now())::date - 3))::timestamp without time zone);


--
-- TOC entry 194 (class 1259 OID 16670)
-- Dependencies: 2239 2240 2241 2242 6
-- Name: parkir_transaksi; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE parkir_transaksi (
    id character varying(20),
    no_pol character varying(20) NOT NULL,
    id_kendaraan character varying(20) NOT NULL,
    status smallint NOT NULL,
    id_pintu_masuk character varying(20),
    id_pintu_keluar character varying(20),
    waktu_masuk timestamp without time zone,
    waktu_keluar timestamp without time zone,
    id_op_masuk character varying(20),
    id_op_keluar character varying(20),
    id_shift_masuk character varying(20),
    id_shift_keluar character varying(20),
    kategori character varying(20),
    status_transaksi character varying(20),
    bayar_masuk double precision,
    bayar_keluar double precision,
    jenis_system character varying(20),
    tanggal timestamp without time zone NOT NULL,
    pic_body_masuk bytea,
    pic_body_keluar bytea,
    pic_driver_masuk bytea,
    pic_driver_keluar bytea,
    pic_no_pol_masuk bytea,
    pic_no_pol_keluar bytea,
    sinkron smallint DEFAULT 0,
    adm character varying(10),
    alasan character varying(200),
    pmlogin timestamp without time zone,
    pklogin timestamp without time zone,
    upload smallint DEFAULT 0,
    manual smallint DEFAULT 0,
    veri_kode character varying(100),
    veri_check smallint,
    veri_adm character varying(50),
    veri_date timestamp without time zone,
    denda double precision,
    extra_bayar double precision,
    no_barcode character varying(30),
    jenis_langganan character varying(20),
    post_pay integer,
    reff_kode character varying,
    valet_adm character varying,
    waktu_valet timestamp without time zone,
    valet_charge integer,
    valet_ops character varying(10),
    valet_nopol character varying(15),
    login_waktu_valet timestamp without time zone,
    cara_bayar integer,
    unit_member character varying(20),
    reserved integer DEFAULT 0,
    no_voucher character varying(32),
    seri_voucher character varying(16),
    no_access_in character varying(64),
    no_access_out character varying(64),
    inap integer
);


--
-- TOC entry 195 (class 1259 OID 16680)
-- Dependencies: 6
-- Name: pass_dump; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE pass_dump (
    notrans character varying(20),
    tgl timestamp without time zone,
    jenis_kendaraan character varying(3),
    nopol character varying(20),
    jml smallint,
    total real,
    status smallint
);


--
-- TOC entry 196 (class 1259 OID 16683)
-- Dependencies: 6
-- Name: pegawai; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE pegawai (
    nomer character varying(50) NOT NULL,
    nama character varying(50) NOT NULL,
    alamat character varying(100),
    tgl_lahir date,
    tgl_masuk date,
    username character varying(50),
    password character varying(50),
    foto bytea,
    bisalogin smallint,
    status smallint,
    jeniskelamin smallint,
    agama character varying(50),
    telepon character varying(255),
    alamat_lahir character varying(255),
    alamat_sekarang character varying(255),
    nip character varying(50),
    statusabsen smallint,
    level_pegawai character varying
);


--
-- TOC entry 2389 (class 0 OID 0)
-- Dependencies: 196
-- Name: TABLE pegawai; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE pegawai IS 'biodata pegawai';


--
-- TOC entry 197 (class 1259 OID 16689)
-- Dependencies: 6
-- Name: pendaftaran; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE pendaftaran (
    notrans character varying(20),
    idcust character varying(20),
    tgl timestamp without time zone,
    adm character varying(10)
);


--
-- TOC entry 198 (class 1259 OID 16692)
-- Dependencies: 6
-- Name: pesan; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE pesan (
    target_pos character varying(50),
    start timestamp without time zone,
    lama integer,
    pesan character varying(1024),
    operator character varying(50),
    tanggal timestamp without time zone,
    id character varying(50)
);


--
-- TOC entry 199 (class 1259 OID 16698)
-- Dependencies: 6
-- Name: pulsa; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE pulsa (
    kode character varying(5),
    harga real,
    point smallint,
    jenis_kendaraan character varying(3),
    masa_aktif smallint
);


--
-- TOC entry 200 (class 1259 OID 16701)
-- Dependencies: 6
-- Name: randomnumber; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE randomnumber (
    used smallint NOT NULL,
    pos character varying(50) NOT NULL,
    number character varying
);


SET default_with_oids = false;

--
-- TOC entry 201 (class 1259 OID 16707)
-- Dependencies: 6
-- Name: reprint; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE reprint (
    petugas character varying(20) NOT NULL,
    id_shift character varying(20) NOT NULL,
    id_pos character varying(20) NOT NULL,
    tanggal timestamp without time zone NOT NULL,
    no_pol character varying(20) NOT NULL,
    waktu_keluar timestamp without time zone NOT NULL,
    pic bytea
);


--
-- TOC entry 202 (class 1259 OID 16713)
-- Dependencies: 2243 2244 2245 2246 2247 6
-- Name: seri_freepas; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE seri_freepas (
    id character varying(10),
    keterangan character varying(30),
    tarif_parkir double precision,
    vc_type integer DEFAULT 0,
    value integer DEFAULT 3,
    mode_tarif integer DEFAULT 0,
    timeperday integer DEFAULT 3,
    maxtarif integer DEFAULT 5000
);


SET default_with_oids = true;

--
-- TOC entry 203 (class 1259 OID 16721)
-- Dependencies: 2248 2249 6
-- Name: setoran; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE setoran (
    no_setoran character varying(50),
    tgl_setoran timestamp without time zone,
    id_penyetor character varying(20),
    shift character varying(20),
    pintu character varying(20),
    setoran_utk_tgl timestamp without time zone,
    jml_uang bigint,
    jml_vaucher smallint,
    id_penerima character varying(20),
    admin character varying(20),
    jml_masalah bigint DEFAULT 0,
    jml_masalah_nilai bigint DEFAULT 0
);


--
-- TOC entry 204 (class 1259 OID 16726)
-- Dependencies: 6
-- Name: shift; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE shift (
    id character varying(50) NOT NULL,
    mulai character varying(50) NOT NULL,
    selama bigint NOT NULL,
    tanggal timestamp without time zone
);


--
-- TOC entry 205 (class 1259 OID 16729)
-- Dependencies: 2000 6
-- Name: simple_transaksi; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW simple_transaksi AS
    SELECT transaksi_parkir.id_op_keluar, transaksi_parkir.id_pintu_keluar, transaksi_parkir.id_shift_keluar, nama_pos.jenis, transaksi_parkir.bayar_keluar, to_char(transaksi_parkir.waktu_keluar, 'MM/DD/YYYY'::text) AS tanggal, transaksi_parkir.veri_check FROM (transaksi_parkir LEFT JOIN nama_pos ON (((nama_pos.id)::text = (transaksi_parkir.id_pintu_masuk)::text))) WHERE (transaksi_parkir.status = 0);


--
-- TOC entry 206 (class 1259 OID 16734)
-- Dependencies: 2001 6
-- Name: simple_parkir_rekap; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW simple_parkir_rekap AS
    SELECT simple_transaksi.id_op_keluar, simple_transaksi.id_pintu_keluar, simple_transaksi.id_shift_keluar, simple_transaksi.jenis, simple_transaksi.tanggal, simple_transaksi.veri_check, sum(simple_transaksi.bayar_keluar) AS sum FROM simple_transaksi GROUP BY simple_transaksi.tanggal, simple_transaksi.id_op_keluar, simple_transaksi.id_pintu_keluar, simple_transaksi.id_shift_keluar, simple_transaksi.jenis, simple_transaksi.veri_check ORDER BY simple_transaksi.tanggal, simple_transaksi.id_op_keluar;


--
-- TOC entry 207 (class 1259 OID 16738)
-- Dependencies: 2002 6
-- Name: simple_transaksi_byshift; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW simple_transaksi_byshift AS
    SELECT transaksi_parkir.id_op_keluar, transaksi_parkir.id_pintu_keluar, transaksi_parkir.id_shift_keluar, nama_pos.jenis, transaksi_parkir.bayar_keluar, to_char(transaksi_parkir.pklogin, 'MM/DD/YYYY'::text) AS tanggal, transaksi_parkir.veri_check FROM (transaksi_parkir LEFT JOIN nama_pos ON (((nama_pos.id)::text = (transaksi_parkir.id_pintu_masuk)::text))) WHERE (transaksi_parkir.status = 0);


--
-- TOC entry 208 (class 1259 OID 16743)
-- Dependencies: 2003 6
-- Name: simple_parkir_rekap_byshift; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW simple_parkir_rekap_byshift AS
    SELECT simple_transaksi_byshift.id_op_keluar, simple_transaksi_byshift.id_pintu_keluar, simple_transaksi_byshift.id_shift_keluar, simple_transaksi_byshift.jenis, simple_transaksi_byshift.tanggal, simple_transaksi_byshift.veri_check, sum(simple_transaksi_byshift.bayar_keluar) AS sum FROM simple_transaksi_byshift GROUP BY simple_transaksi_byshift.tanggal, simple_transaksi_byshift.id_op_keluar, simple_transaksi_byshift.id_pintu_keluar, simple_transaksi_byshift.id_shift_keluar, simple_transaksi_byshift.jenis, simple_transaksi_byshift.veri_check ORDER BY simple_transaksi_byshift.tanggal, simple_transaksi_byshift.id_op_keluar;


--
-- TOC entry 209 (class 1259 OID 16747)
-- Dependencies: 2250 6
-- Name: softseting; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE softseting (
    namasoft character varying(255) NOT NULL,
    versoft character varying(50) NOT NULL,
    namasystem character varying(255) NOT NULL,
    versystem character varying(50) NOT NULL,
    namaperusahaan character varying(255) NOT NULL,
    alamat character varying(255) NOT NULL,
    telepon character varying(255),
    namalokasi character varying(255) NOT NULL,
    alamatlokasi character varying(255) NOT NULL,
    softplatform smallint NOT NULL,
    lisensi smallint NOT NULL,
    period real,
    tipesoft smallint NOT NULL,
    banyakclient bigint NOT NULL,
    logo bytea,
    tanggal timestamp without time zone,
    parkintf smallint,
    npwp character varying(50),
    nppkp character varying(50),
    smson smallint DEFAULT 0,
    mail_name character varying(25),
    mail_address character varying(50),
    incom_mail character varying(25),
    out_mail character varying(25),
    pasw_mail character varying(25),
    stok_awal smallint,
    stok_kunci timestamp without time zone,
    cabang_lokasi character varying(50)
);


--
-- TOC entry 210 (class 1259 OID 16754)
-- Dependencies: 2251 6
-- Name: stasiunkerja; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE stasiunkerja (
    kode character varying(50) NOT NULL,
    nama character varying(255) NOT NULL,
    margin smallint DEFAULT 0,
    spv character varying(20),
    target smallint,
    contact character varying,
    alamat character varying,
    alamat1 character varying,
    alamat2 character varying,
    tntcd character varying,
    rntno character varying
);


SET default_with_oids = false;

--
-- TOC entry 211 (class 1259 OID 16761)
-- Dependencies: 6
-- Name: stok_barcode; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE stok_barcode (
    code character varying(50),
    status smallint,
    no character varying
);


SET default_with_oids = true;

--
-- TOC entry 212 (class 1259 OID 16767)
-- Dependencies: 6
-- Name: stokkartu; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE stokkartu (
    idcard character varying(15),
    lokasi character varying(2),
    kendaraan character varying(2),
    status smallint,
    nopol character varying(32),
    waktu_masuk timestamp without time zone,
    tanggal timestamp without time zone,
    shift character varying(16),
    tgl_trans timestamp without time zone
);


--
-- TOC entry 213 (class 1259 OID 16770)
-- Dependencies: 2252 2253 2254 2255 6
-- Name: tarif; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE tarif (
    id_mobil character varying(50) NOT NULL,
    tarif double precision NOT NULL,
    tarif_interval double precision,
    "interval" integer,
    waktu_tarif integer,
    waktu_gratis integer,
    bayar_dimuka smallint,
    denda double precision,
    maksimum double precision,
    tanggal timestamp without time zone,
    tarif2 double precision,
    waktu2 integer,
    tarif_period double precision,
    max_per_hari smallint,
    min_per_hari integer,
    time_base smallint,
    tarif_inap smallint,
    batas_min_inap character varying,
    max_kena_charge character varying,
    tarif_member smallint,
    tarif_voucher bigint,
    voucher_frek smallint,
    voucher_time smallint,
    voucher_base smallint,
    voucher_base_time smallint,
    asuransi_incl double precision,
    denda_only_casual smallint,
    frek_interval integer,
    frek_waktu2 integer,
    free_for_validasi smallint,
    time_base_maks integer,
    free_pos_default integer,
    tarif_valet integer,
    type_tarif_member integer,
    start_time_member_charge character varying,
    stop_time_member_charge character varying,
    min_time_tarif_member integer,
    batas_inap_min integer,
    periode_inap integer,
    free_same_day integer,
    valet_extra_time integer DEFAULT 0,
    extra_charge_value integer DEFAULT 0,
    extra_charge_time integer DEFAULT 0,
    tarif3 double precision,
    waktu3 integer,
    frek_waktu3 integer,
    denda_member integer,
    denda_only integer DEFAULT 0,
    gratis_waktu_tertentu integer,
    start_gratis_waktu_tertentu character varying(5),
    stop_gratis_waktu_tertentu character varying(5),
    tarif_member_valid_pos character varying(30),
    free_same_hour integer,
    max_free_same_hour integer
);


--
-- TOC entry 214 (class 1259 OID 16780)
-- Dependencies: 6
-- Name: tarif_inap; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE tarif_inap (
    id_mobil character varying(50) NOT NULL,
    tarif_member double precision NOT NULL,
    tarif_interval double precision,
    "interval" integer,
    waktu_tarif integer,
    waktu_gratis integer,
    bayar_dimuka smallint,
    denda double precision,
    maksimum double precision,
    tanggal timestamp without time zone
);


--
-- TOC entry 215 (class 1259 OID 16783)
-- Dependencies: 6
-- Name: tarif_member; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE tarif_member (
    id_mobil character varying(50) NOT NULL,
    tarif double precision NOT NULL,
    tarif_interval double precision,
    "interval" integer,
    waktu_tarif integer,
    waktu_gratis integer,
    bayar_dimuka smallint,
    denda double precision,
    maksimum double precision,
    tanggal timestamp without time zone,
    tarif2 double precision,
    waktu2 integer,
    tarif_period double precision,
    max_per_hari smallint
);


--
-- TOC entry 216 (class 1259 OID 16786)
-- Dependencies: 6
-- Name: tarif_rest; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE tarif_rest (
    id_mobil character varying(50) NOT NULL,
    tarif double precision NOT NULL,
    tarif_interval double precision,
    "interval" integer,
    waktu_tarif integer,
    waktu_gratis integer,
    bayar_dimuka smallint,
    denda double precision,
    maksimum double precision,
    tanggal timestamp without time zone,
    tarif2 double precision,
    waktu2 integer,
    tarif_period double precision,
    max_per_hari smallint,
    min_per_hari integer,
    time_base smallint,
    adm character varying(50),
    tarif_inap bigint,
    time_base_maks integer
);


SET default_with_oids = false;

--
-- TOC entry 217 (class 1259 OID 16789)
-- Dependencies: 6
-- Name: tarif_stiker; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE tarif_stiker (
    id_mobil character varying(10) NOT NULL,
    jenis_langganan character varying(50) NOT NULL,
    tarif double precision NOT NULL,
    masa_berlaku integer,
    toleransi integer,
    bayar_inap integer,
    biaya_inap integer,
    awal_kena_inap character varying,
    akhir_kena_inap character varying,
    biaya_inap_berlaku integer
);


--
-- TOC entry 218 (class 1259 OID 16795)
-- Dependencies: 6
-- Name: tiket_masalah; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE tiket_masalah (
    id character varying(25),
    keterangan character varying(50)
);


--
-- TOC entry 219 (class 1259 OID 16798)
-- Dependencies: 2004 6
-- Name: transaction; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW transaction AS
    SELECT tr.id, tr.waktu_masuk, tr.waktu_keluar, tr.no_pol, jenis_mobil.nama, (CASE WHEN (length((tr.veri_kode)::text) > 0) THEN (0)::double precision ELSE tr.bayar_keluar END + CASE WHEN (tr.bayar_masuk IS NULL) THEN (0)::double precision ELSE tr.bayar_masuk END) AS bayar, 0 AS amount2, 0 AS amount3, 0 AS amount4, 0 AS amount5, 0 AS amount6, 0 AS amount7, 0 AS amount8 FROM (parkir_transaksi tr LEFT JOIN jenis_mobil ON (((tr.id_kendaraan)::text = (jenis_mobil.id)::text))) WHERE ((tr.status = 0) AND ((tr.status_transaksi)::text = ANY (ARRAY[('0'::character varying)::text, ('1'::character varying)::text, ('2'::character varying)::text, ('3'::character varying)::text, ('32'::character varying)::text])));


--
-- TOC entry 220 (class 1259 OID 16803)
-- Dependencies: 2005 6
-- Name: transaction_member; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW transaction_member AS
    SELECT transaksi_stiker.notrans, transaksi_stiker.awal, transaksi_stiker.akhir, (SELECT detail_transaksi_stiker.nopol FROM detail_transaksi_stiker WHERE ((detail_transaksi_stiker.notrans)::text = (transaksi_stiker.notrans)::text) LIMIT 1) AS nopol, (SELECT jenis_mobil.nama FROM (detail_transaksi_stiker LEFT JOIN jenis_mobil ON (((jenis_mobil.id)::text = (detail_transaksi_stiker.jenis_mobil)::text))) WHERE ((detail_transaksi_stiker.notrans)::text = (transaksi_stiker.notrans)::text) LIMIT 1) AS nama, transaksi_stiker.harga, 0 AS amount2, 0 AS amount3, 0 AS amount4, 0 AS amount5, 0 AS amount6, 0 AS amount7, 0 AS amount8 FROM transaksi_stiker;


--
-- TOC entry 221 (class 1259 OID 16808)
-- Dependencies: 2006 6
-- Name: transaction_void; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW transaction_void AS
    SELECT tr.id, tr.waktu_masuk, tr.waktu_keluar, tr.no_pol, jenis_mobil.nama, (CASE WHEN (length((tr.veri_kode)::text) > 0) THEN (0)::double precision ELSE tr.bayar_keluar END + CASE WHEN (tr.bayar_masuk IS NULL) THEN (0)::double precision ELSE tr.bayar_masuk END) AS bayar, 0 AS amount2, 0 AS amount3, 0 AS amount4, 0 AS amount5, 0 AS amount6, 0 AS amount7, 0 AS amount8 FROM (parkir_transaksi tr LEFT JOIN jenis_mobil ON (((tr.id_kendaraan)::text = (jenis_mobil.id)::text))) WHERE ((tr.status = 0) AND (((tr.status_transaksi)::text = '-1'::text) OR (tr.cara_bayar <> 0)));


SET default_with_oids = true;

--
-- TOC entry 222 (class 1259 OID 16813)
-- Dependencies: 6
-- Name: transaksi_gantiid; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE transaksi_gantiid (
    notrans character varying(15),
    nopol character varying(20),
    idlama character varying(20),
    idbaru character varying(20),
    jenis_kendaraan character varying(3),
    tgl timestamp without time zone,
    total real,
    adm character varying(20),
    idcust character varying(20)
);


SET default_with_oids = false;

--
-- TOC entry 223 (class 1259 OID 16816)
-- Dependencies: 2256 6
-- Name: transaksi_inap; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE transaksi_inap (
    id character varying(16),
    no_pol character varying(32),
    waktu_masuk timestamp without time zone,
    waktu_daftar timestamp without time zone,
    rencana_keluar timestamp without time zone,
    nama character varying(255),
    alamat character varying(1024),
    telepon character varying(64),
    bayar integer,
    open integer DEFAULT 0,
    adm character varying(10)
);


SET default_with_oids = true;

--
-- TOC entry 224 (class 1259 OID 16823)
-- Dependencies: 6
-- Name: transaksi_masalah; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE transaksi_masalah (
    notrans character varying(50),
    nopol character varying(50),
    adm character varying(50),
    alasan character varying(250),
    shift character varying(50),
    pos character varying(50),
    tanggal timestamp without time zone,
    waktu_masuk timestamp without time zone
);


SET default_with_oids = false;

--
-- TOC entry 225 (class 1259 OID 16829)
-- Dependencies: 6
-- Name: transaksi_parkir_driver; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE transaksi_parkir_driver (
    id character varying(10) NOT NULL,
    no_pol character varying(32) NOT NULL,
    waktu_masuk timestamp without time zone NOT NULL,
    nama character varying(255) NOT NULL,
    ktp character varying(255) NOT NULL,
    alamat character varying(255),
    stnk character varying(255),
    kendaraan character varying(255),
    warna character varying(255),
    vendor character varying(64),
    index_muatan integer,
    catatan1 character varying(255),
    catatan2 character varying(255),
    bonus integer,
    id_trans character varying(64)
);


SET default_with_oids = true;

--
-- TOC entry 226 (class 1259 OID 16835)
-- Dependencies: 6
-- Name: transaksi_parkir_gambar; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE transaksi_parkir_gambar (
    notrans character varying(10),
    waktu timestamp without time zone,
    id_pos character varying(5),
    gambar_body bytea,
    gambar_driver bytea
);


--
-- TOC entry 227 (class 1259 OID 16841)
-- Dependencies: 2257 6
-- Name: transaksi_parkir_inap; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE transaksi_parkir_inap (
    id character varying(20) NOT NULL,
    no_pol character varying(20) NOT NULL,
    id_kendaraan character varying(20) NOT NULL,
    status smallint NOT NULL,
    id_pintu_masuk character varying(20),
    id_pintu_keluar character varying(20),
    waktu_masuk timestamp without time zone,
    waktu_keluar timestamp without time zone,
    id_op_masuk character varying(20),
    id_op_keluar character varying(20),
    id_shift_masuk character varying(20),
    id_shift_keluar character varying(20),
    kategori character varying(20),
    status_transaksi character varying(20),
    bayar_masuk double precision,
    bayar_keluar double precision,
    jenis_system character varying(20),
    tanggal timestamp without time zone NOT NULL,
    pic_body_masuk bytea,
    pic_body_keluar bytea,
    pic_driver_masuk bytea,
    pic_driver_keluar bytea,
    pic_no_pol_masuk bytea,
    pic_no_pol_keluar bytea,
    sinkron smallint DEFAULT 0
);


--
-- TOC entry 228 (class 1259 OID 16848)
-- Dependencies: 2258 6
-- Name: transaksi_pulsa; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE transaksi_pulsa (
    notrans character varying(20),
    idcust character varying(20),
    tgl timestamp without time zone,
    adm character varying,
    upload smallint DEFAULT 0
);


--
-- TOC entry 229 (class 1259 OID 16855)
-- Dependencies: 2259 6
-- Name: transaksi_stiker_res; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE transaksi_stiker_res (
    notrans character varying(50) NOT NULL,
    nama character varying(50),
    alamat character varying(50),
    telepon character varying(50),
    jenis_transaksi smallint,
    awal timestamp without time zone,
    harga double precision,
    keterangan character varying(255),
    tanggal timestamp without time zone,
    operator character varying(50),
    akhir timestamp without time zone,
    maks smallint DEFAULT 1,
    no_id character varying(30),
    unit_kerja character varying(20),
    no_induk character varying(25),
    nopol character varying(50),
    jenis_mobil character varying(50),
    adm character varying(10)
);


SET default_with_oids = false;

--
-- TOC entry 230 (class 1259 OID 16862)
-- Dependencies: 2260 6
-- Name: valet; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE valet (
    id character varying(16),
    nopol character varying(16),
    waktu_daftar_in timestamp without time zone,
    adm_daftar_in character varying(16),
    waktu_driver_in timestamp without time zone,
    id_driver_in character varying(16),
    waktu_parkir timestamp without time zone,
    lot_parkir character varying(16),
    waktu_daftar_out timestamp without time zone,
    adm_daftar_out character varying(16),
    waktu_driver_out timestamp without time zone,
    id_driver_out character varying,
    waktu_serah_terima timestamp without time zone,
    valet_tarif integer,
    parkir_tarif integer,
    barcode character varying(64),
    akses_id_in character varying(16),
    akses_id_out character varying(16),
    adm_in_login timestamp without time zone,
    driver_in_login timestamp without time zone,
    adm_out_login timestamp without time zone,
    driver_out_login timestamp without time zone,
    shift_adm_in character varying(16),
    shift_driver_in character varying(16),
    shift_adm_out character varying(16),
    adm_driver_out character varying(16),
    denda_tarif integer DEFAULT 0,
    status smallint,
    no_reff character varying,
    keterangan character varying,
    barang_di_mobil character varying,
    id_pos_in character varying,
    id_pos_out character varying
);


--
-- TOC entry 231 (class 1259 OID 16869)
-- Dependencies: 6
-- Name: valet_cust_info; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE valet_cust_info (
    nopol character varying(16) NOT NULL,
    nama character varying(64),
    merek character varying(32),
    warna character varying(32)
);


--
-- TOC entry 232 (class 1259 OID 16872)
-- Dependencies: 6
-- Name: valet_out; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE valet_out (
    notrans character varying(50),
    valet_nopol character varying(50),
    barcode character varying(50),
    waktu_keluar timestamp without time zone,
    waktu_masuk timestamp without time zone,
    valet_charge double precision,
    valet_adm character varying(10),
    waktu_valet timestamp without time zone,
    valet_ops character varying(10),
    login_waktu_valet timestamp without time zone,
    jenis_valet_out integer
);


SET default_with_oids = true;

--
-- TOC entry 233 (class 1259 OID 16875)
-- Dependencies: 6
-- Name: video_counter; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE video_counter (
    id_pos character varying(50) NOT NULL,
    tanggal timestamp without time zone NOT NULL,
    counter integer,
    data bytea
);


--
-- TOC entry 234 (class 1259 OID 16881)
-- Dependencies: 6
-- Name: vod; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE vod (
    host character varying(50) NOT NULL,
    tanggal timestamp without time zone NOT NULL,
    input integer,
    data bytea
);


--
-- TOC entry 2293 (class 0 OID 16399)
-- Dependencies: 140
-- Data for Name: agama; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO agama (kode, nama) VALUES ('0001', 'Islam');
INSERT INTO agama (kode, nama) VALUES ('0002', 'Katolik');
INSERT INTO agama (kode, nama) VALUES ('0003', 'Protestan');
INSERT INTO agama (kode, nama) VALUES ('0004', 'Hindu');
INSERT INTO agama (kode, nama) VALUES ('0005', 'Budha');


--
-- TOC entry 2294 (class 0 OID 16402)
-- Dependencies: 141
-- Data for Name: aksespegawai; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO aksespegawai (form, password, status, idcard) VALUES (10013, '', 1, '00001');
INSERT INTO aksespegawai (form, password, status, idcard) VALUES (10015, '', 1, '00001');
INSERT INTO aksespegawai (form, password, status, idcard) VALUES (10016, '', 1, '00001');
INSERT INTO aksespegawai (form, password, status, idcard) VALUES (10013, '', 1, '001');
INSERT INTO aksespegawai (form, password, status, idcard) VALUES (10015, '', 1, '001');
INSERT INTO aksespegawai (form, password, status, idcard) VALUES (10013, '', 1, '00004');
INSERT INTO aksespegawai (form, password, status, idcard) VALUES (10015, '', 1, '00004');
INSERT INTO aksespegawai (form, password, status, idcard) VALUES (10013, '', 1, '0001');
INSERT INTO aksespegawai (form, password, status, idcard) VALUES (10015, '', 1, '0001');
INSERT INTO aksespegawai (form, password, status, idcard) VALUES (10016, '', 1, '0001');
INSERT INTO aksespegawai (form, password, status, idcard) VALUES (10017, '', 1, '0001');
INSERT INTO aksespegawai (form, password, status, idcard) VALUES (10018, '', 1, '0001');


--
-- TOC entry 2295 (class 0 OID 16405)
-- Dependencies: 142
-- Data for Name: aksestable; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO aksestable (idcard, idform) VALUES ('04', 1);
INSERT INTO aksestable (idcard, idform) VALUES ('04', 2);
INSERT INTO aksestable (idcard, idform) VALUES ('04', 3);
INSERT INTO aksestable (idcard, idform) VALUES ('04', 200000);
INSERT INTO aksestable (idcard, idform) VALUES ('04', 200001);
INSERT INTO aksestable (idcard, idform) VALUES ('04', 200006);
INSERT INTO aksestable (idcard, idform) VALUES ('04', 200007);
INSERT INTO aksestable (idcard, idform) VALUES ('04', 500000);
INSERT INTO aksestable (idcard, idform) VALUES ('04', 500001);
INSERT INTO aksestable (idcard, idform) VALUES ('04', 500010);
INSERT INTO aksestable (idcard, idform) VALUES ('04', 500200);
INSERT INTO aksestable (idcard, idform) VALUES ('04', 500211);
INSERT INTO aksestable (idcard, idform) VALUES ('04', 500213);
INSERT INTO aksestable (idcard, idform) VALUES ('04', 500220);
INSERT INTO aksestable (idcard, idform) VALUES ('03', 1);
INSERT INTO aksestable (idcard, idform) VALUES ('03', 2);
INSERT INTO aksestable (idcard, idform) VALUES ('03', 3);
INSERT INTO aksestable (idcard, idform) VALUES ('03', 200000);
INSERT INTO aksestable (idcard, idform) VALUES ('03', 200001);
INSERT INTO aksestable (idcard, idform) VALUES ('03', 200006);
INSERT INTO aksestable (idcard, idform) VALUES ('03', 200007);
INSERT INTO aksestable (idcard, idform) VALUES ('03', 500000);
INSERT INTO aksestable (idcard, idform) VALUES ('03', 500001);
INSERT INTO aksestable (idcard, idform) VALUES ('03', 500010);
INSERT INTO aksestable (idcard, idform) VALUES ('03', 500113);
INSERT INTO aksestable (idcard, idform) VALUES ('03', 500200);
INSERT INTO aksestable (idcard, idform) VALUES ('03', 500211);
INSERT INTO aksestable (idcard, idform) VALUES ('03', 500220);
INSERT INTO aksestable (idcard, idform) VALUES ('02', 1);
INSERT INTO aksestable (idcard, idform) VALUES ('02', 2);
INSERT INTO aksestable (idcard, idform) VALUES ('02', 3);
INSERT INTO aksestable (idcard, idform) VALUES ('02', 200000);
INSERT INTO aksestable (idcard, idform) VALUES ('02', 200001);
INSERT INTO aksestable (idcard, idform) VALUES ('02', 200007);
INSERT INTO aksestable (idcard, idform) VALUES ('02', 500000);
INSERT INTO aksestable (idcard, idform) VALUES ('02', 500001);
INSERT INTO aksestable (idcard, idform) VALUES ('02', 500010);
INSERT INTO aksestable (idcard, idform) VALUES ('02', 500200);
INSERT INTO aksestable (idcard, idform) VALUES ('02', 500211);
INSERT INTO aksestable (idcard, idform) VALUES ('02', 500220);
INSERT INTO aksestable (idcard, idform) VALUES ('02', 200006);
INSERT INTO aksestable (idcard, idform) VALUES ('02', 500113);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 1);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 2);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 3);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 100000);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 100001);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 100002);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 100003);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 100004);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 100005);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 100006);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 100007);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 100009);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 100010);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 100017);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 100018);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 100019);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 100020);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 100021);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 100022);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 200000);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 200001);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 200002);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 200003);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 200004);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 200005);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 200006);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 200007);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 200008);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 200009);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 200015);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 200016);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 200017);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 400000);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 400001);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 400002);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 500000);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 500001);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 500002);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 500003);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 500004);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 500005);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 500008);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 500009);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 500010);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 500011);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 500014);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 500015);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 500019);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 500110);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 500111);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 500112);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 500113);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 500120);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 500121);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 500122);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 500200);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 500204);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 500210);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 500211);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 500212);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 500213);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 500220);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 500221);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 500230);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 500231);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 500240);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 500241);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 710000);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 710002);
INSERT INTO aksestable (idcard, idform) VALUES ('01', 500214);
INSERT INTO aksestable (idcard, idform) VALUES ('0005', 1);
INSERT INTO aksestable (idcard, idform) VALUES ('0005', 2);
INSERT INTO aksestable (idcard, idform) VALUES ('0005', 3);
INSERT INTO aksestable (idcard, idform) VALUES ('0002', 1);
INSERT INTO aksestable (idcard, idform) VALUES ('0002', 2);
INSERT INTO aksestable (idcard, idform) VALUES ('0002', 3);
INSERT INTO aksestable (idcard, idform) VALUES ('0002', 500000);
INSERT INTO aksestable (idcard, idform) VALUES ('0002', 500001);
INSERT INTO aksestable (idcard, idform) VALUES ('0002', 500111);
INSERT INTO aksestable (idcard, idform) VALUES ('0002', 500200);
INSERT INTO aksestable (idcard, idform) VALUES ('0002', 500217);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 1);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 100000);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 100001);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 100003);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 100004);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 100005);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 100006);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 100009);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 100010);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 100017);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 100018);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 100019);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 100021);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 100022);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 2);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 200000);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 200001);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 200002);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 200003);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 200004);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 200006);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 200007);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 200008);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 200015);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 200016);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 200017);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 3);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 500000);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 500001);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 500002);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 500003);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 500004);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 500005);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 500008);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 500009);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 500010);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 500011);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 500014);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 500015);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 500110);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 500111);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 500112);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 500113);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 500120);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 500121);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 500122);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 500200);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 500204);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 500210);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 500211);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 500212);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 500213);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 500220);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 500221);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 500230);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 500231);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 500240);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 500241);
INSERT INTO aksestable (idcard, idform) VALUES ('00001', 500214);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 1);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 2);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 100000);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 100001);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 100003);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 100004);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 100005);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 100006);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 100007);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 100009);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 100010);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 100017);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 100018);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 100019);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 100021);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 100022);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 100030);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 200000);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 200001);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 200002);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 200003);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 200004);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 200006);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 200007);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 200008);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 200015);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 200016);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 200017);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 400000);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 500000);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 500001);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 500002);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 500003);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 500004);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 500005);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 500008);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 500009);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 500010);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 500011);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 500014);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 500015);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 500016);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 500018);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 500110);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 500111);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 500112);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 500120);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 500121);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 500122);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 500200);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 500204);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 500210);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 500211);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 500212);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 500213);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 500214);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 500216);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 500220);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 500221);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 500224);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 500230);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 500231);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 500240);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 500241);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 500242);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 200022);
INSERT INTO aksestable (idcard, idform) VALUES ('0001', 200023);


--
-- TOC entry 2296 (class 0 OID 16408)
-- Dependencies: 143
-- Data for Name: biaya_admin; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2297 (class 0 OID 16411)
-- Dependencies: 144
-- Data for Name: biaya_poin; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2298 (class 0 OID 16414)
-- Dependencies: 145
-- Data for Name: blacklist_kendaraan; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2299 (class 0 OID 16420)
-- Dependencies: 146
-- Data for Name: card_member; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2300 (class 0 OID 16426)
-- Dependencies: 147
-- Data for Name: card_member_rest; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2301 (class 0 OID 16434)
-- Dependencies: 149
-- Data for Name: config_file; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO config_file (exit_pass, jam_malam_mulai, jam_malam_selesai, pengguna_exit_pass, footer_in_1, footer_in_3, footer_in_2, footer_out_1, footer_out_2, footer_out_3, cetak_tambahan_in, cetak_tambahan_out) VALUES (0, '  :  :  ', '  :  :  ', 0, 'JANGAN TINGGALKAN BARANG BERHARGA', '', 'DIDALAM KENDARAAN ANDA', '', '', '', NULL, NULL);


--
-- TOC entry 2302 (class 0 OID 16440)
-- Dependencies: 150
-- Data for Name: config_pos; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO config_pos (prefix, max_load_index, camera_refresh, max_nopol_avail, max_nopol, max_member_on_a_time, message, info_member, ploting, info_volume, login_a_time, tiket_masalah, use_barcode, warning_member, start_warning_member, add_barcode_struk_in, type_barcode_struk_in, input_kode_pisah, cek_mobil_masalah, overwrite, no_reinput, pos_for_any_kode, any_kode, confirm_input, akses_for_reprint, no_input_notrans, only_input_any_digit, any_digit, input_notrans_only_open_gate, max_input_notrans, max_input_notrans_value, autoprint_struk, reprint_struk_activ, no_reinput_out, id_pos, shortcut_kode, footer1, footer2, cetak_tambahan, ouc, ouc_tipe_barcode, footer3, footer4, kend_valid, swapable, id_pos_alternative, manual_bg_enable, disable_manual, enable_icmp, show_print_counter, detail_muatan, soe, lbi, falidasi_instant, print_total_nol, iuc, vericode_unix, limit_validasi, form_denda, customer_counter, debug_window, aktivasi_voucher, interval_time_member, min_interval_time_member) VALUES ('DD', 250, 0, 1, 12, 0, 0, 1, 0, 0, 0, 0, 0, 0, 7, NULL, NULL, 1, 1, 0, 1, 0, 'C', 2, 1, 0, 1, 2, 1, 1, 3, 1, 1, 1, 'PK2', 'C', '', '', '', 1, 0, '', '', 'A,C,D', 0, 'null', 1, 0, 0, NULL, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, NULL, 0, NULL, NULL);
INSERT INTO config_pos (prefix, max_load_index, camera_refresh, max_nopol_avail, max_nopol, max_member_on_a_time, message, info_member, ploting, info_volume, login_a_time, tiket_masalah, use_barcode, warning_member, start_warning_member, add_barcode_struk_in, type_barcode_struk_in, input_kode_pisah, cek_mobil_masalah, overwrite, no_reinput, pos_for_any_kode, any_kode, confirm_input, akses_for_reprint, no_input_notrans, only_input_any_digit, any_digit, input_notrans_only_open_gate, max_input_notrans, max_input_notrans_value, autoprint_struk, reprint_struk_activ, no_reinput_out, id_pos, shortcut_kode, footer1, footer2, cetak_tambahan, ouc, ouc_tipe_barcode, footer3, footer4, kend_valid, swapable, id_pos_alternative, manual_bg_enable, disable_manual, enable_icmp, show_print_counter, detail_muatan, soe, lbi, falidasi_instant, print_total_nol, iuc, vericode_unix, limit_validasi, form_denda, customer_counter, debug_window, aktivasi_voucher, interval_time_member, min_interval_time_member) VALUES ('DD', 250, 0, 1, 12, 0, 0, 1, 0, 0, 0, 0, 0, 0, 7, NULL, NULL, 1, 1, 0, 1, 0, 'A', 2, 1, 0, 1, 2, 1, 1, 3, 1, 1, 1, 'PK1', 'A', '', '', '', 1, 0, '', '', 'A,C,D', 0, 'null', 1, 0, 0, NULL, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, NULL, 0, NULL, NULL);
INSERT INTO config_pos (prefix, max_load_index, camera_refresh, max_nopol_avail, max_nopol, max_member_on_a_time, message, info_member, ploting, info_volume, login_a_time, tiket_masalah, use_barcode, warning_member, start_warning_member, add_barcode_struk_in, type_barcode_struk_in, input_kode_pisah, cek_mobil_masalah, overwrite, no_reinput, pos_for_any_kode, any_kode, confirm_input, akses_for_reprint, no_input_notrans, only_input_any_digit, any_digit, input_notrans_only_open_gate, max_input_notrans, max_input_notrans_value, autoprint_struk, reprint_struk_activ, no_reinput_out, id_pos, shortcut_kode, footer1, footer2, cetak_tambahan, ouc, ouc_tipe_barcode, footer3, footer4, kend_valid, swapable, id_pos_alternative, manual_bg_enable, disable_manual, enable_icmp, show_print_counter, detail_muatan, soe, lbi, falidasi_instant, print_total_nol, iuc, vericode_unix, limit_validasi, form_denda, customer_counter, debug_window, aktivasi_voucher, interval_time_member, min_interval_time_member) VALUES ('DD', 250, 0, 1, 12, 0, 0, 1, 0, 0, 0, 0, 0, 0, 7, NULL, NULL, 1, 0, 0, 1, 0, 'A', 0, 1, 0, 1, 2, 1, 1, 3, 0, 1, 0, '01', 'A', '', '', '', 1, 0, '', '', 'A,C,D', 0, 'null', 1, 0, 0, NULL, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, NULL, 0, NULL, NULL);
INSERT INTO config_pos (prefix, max_load_index, camera_refresh, max_nopol_avail, max_nopol, max_member_on_a_time, message, info_member, ploting, info_volume, login_a_time, tiket_masalah, use_barcode, warning_member, start_warning_member, add_barcode_struk_in, type_barcode_struk_in, input_kode_pisah, cek_mobil_masalah, overwrite, no_reinput, pos_for_any_kode, any_kode, confirm_input, akses_for_reprint, no_input_notrans, only_input_any_digit, any_digit, input_notrans_only_open_gate, max_input_notrans, max_input_notrans_value, autoprint_struk, reprint_struk_activ, no_reinput_out, id_pos, shortcut_kode, footer1, footer2, cetak_tambahan, ouc, ouc_tipe_barcode, footer3, footer4, kend_valid, swapable, id_pos_alternative, manual_bg_enable, disable_manual, enable_icmp, show_print_counter, detail_muatan, soe, lbi, falidasi_instant, print_total_nol, iuc, vericode_unix, limit_validasi, form_denda, customer_counter, debug_window, aktivasi_voucher, interval_time_member, min_interval_time_member) VALUES ('DD', 250, 0, 1, 12, 0, 0, 1, 0, 0, 0, 0, 0, 0, 7, NULL, NULL, 1, 0, 0, 1, 0, 'C', 0, 1, 0, 1, 2, 1, 1, 3, 1, 1, 1, '02', 'C', '', '', '', 1, 0, '', '', 'A,C,D', 0, 'null', 1, 0, 0, NULL, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, NULL, 0, NULL, NULL);


--
-- TOC entry 2303 (class 0 OID 16457)
-- Dependencies: 151
-- Data for Name: config_pos_hardware; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO config_pos_hardware (printer1_avail, printer1_conn, printer1_spd, printer1_stdfile, printer1_autocutter, printer1_bgconnect, printer1_dummy, video1_avail, video1_conn, video1_channel, video1_version, feedisplay_avail, feedisplay_conn, feedisplay_paralel, feedisplay_version, bg_avail, bg_conn, bg_paralel, bg_value, sound_avail, sound_conn, sound_version, sound_partisi, id_pos, sizeable, pjg_lcd, video1_bright, video2_avail, video2_conn, video2_channel, video2_version, video2_bright, video2_sizeable, smartcard_avail, smartcard_speed, smartcard_port, printer2_avail, printer2_conn, printer2_spd, printer2_stdfile, printer2_autocutter, printer2_bgconnect, printer2_dummy, fan1_maxval, fan2_maxval, temp1_maxval, temp2_maxval, sensor_fan1, sensor_fan2, sensor_temp1, sensor_temp2, bg_type, bg_usb, video3_avail, video3_conn, video3_channel, video3_version, video3_bright, video3_sizeable) VALUES (1, '/dev/usb/lp0', '9600', 1, 1, 0, 0, 0, 'http://192.168.10.202:81/snapshot.cgi?user=admin&pwd=888888', 0, 0, 0, 'COM1', '0', 0, 1, '/dev/ttyS0', 0, 85, 0, '/dev/dsp', 0, 0, 'PK1', 0, 16, '', 0, '', 0, 0, '', 0, 0, 0, 'USB:', 0, '', '', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, NULL, 0, 0, '', 0, 0, '', 0);
INSERT INTO config_pos_hardware (printer1_avail, printer1_conn, printer1_spd, printer1_stdfile, printer1_autocutter, printer1_bgconnect, printer1_dummy, video1_avail, video1_conn, video1_channel, video1_version, feedisplay_avail, feedisplay_conn, feedisplay_paralel, feedisplay_version, bg_avail, bg_conn, bg_paralel, bg_value, sound_avail, sound_conn, sound_version, sound_partisi, id_pos, sizeable, pjg_lcd, video1_bright, video2_avail, video2_conn, video2_channel, video2_version, video2_bright, video2_sizeable, smartcard_avail, smartcard_speed, smartcard_port, printer2_avail, printer2_conn, printer2_spd, printer2_stdfile, printer2_autocutter, printer2_bgconnect, printer2_dummy, fan1_maxval, fan2_maxval, temp1_maxval, temp2_maxval, sensor_fan1, sensor_fan2, sensor_temp1, sensor_temp2, bg_type, bg_usb, video3_avail, video3_conn, video3_channel, video3_version, video3_bright, video3_sizeable) VALUES (1, '/dev/usb/lp0', '9600', 1, 1, 0, 0, 0, '/dev/video0', 0, 0, 0, 'COM1', '0', 0, 1, '/dev/ttyS0', 0, 85, 0, '/dev/dsp', 0, 0, 'PK2', 0, 16, '0', 0, '/dev/video0', 0, 0, '0', 0, 0, 9600, 'USB:COM1', 0, '/dev/ttyS1', '9600', 1, 1, 0, 0, 10, 10, 10, 10, 0, 0, 0, 0, NULL, 0, 0, '/dev/video0', 0, 0, '0', 0);
INSERT INTO config_pos_hardware (printer1_avail, printer1_conn, printer1_spd, printer1_stdfile, printer1_autocutter, printer1_bgconnect, printer1_dummy, video1_avail, video1_conn, video1_channel, video1_version, feedisplay_avail, feedisplay_conn, feedisplay_paralel, feedisplay_version, bg_avail, bg_conn, bg_paralel, bg_value, sound_avail, sound_conn, sound_version, sound_partisi, id_pos, sizeable, pjg_lcd, video1_bright, video2_avail, video2_conn, video2_channel, video2_version, video2_bright, video2_sizeable, smartcard_avail, smartcard_speed, smartcard_port, printer2_avail, printer2_conn, printer2_spd, printer2_stdfile, printer2_autocutter, printer2_bgconnect, printer2_dummy, fan1_maxval, fan2_maxval, temp1_maxval, temp2_maxval, sensor_fan1, sensor_fan2, sensor_temp1, sensor_temp2, bg_type, bg_usb, video3_avail, video3_conn, video3_channel, video3_version, video3_bright, video3_sizeable) VALUES (1, '/dev/usb/lp0', '9600', 1, 1, 0, 0, 0, '/dev/video0', 0, 0, 0, 'COM1', '0', 0, 0, 'COM1', 0, 85, 0, '/dev/dsp', 0, 0, '02', 0, 16, '0', 0, '/dev/video0', 0, 0, '0', 0, 0, 9600, 'USB:COM1', 0, '/dev/ttyS1', '9600', 1, 1, 0, 0, 10, 10, 10, 10, 0, 0, 0, 0, NULL, 0, 0, '/dev/video0', 0, 0, '0', 0);
INSERT INTO config_pos_hardware (printer1_avail, printer1_conn, printer1_spd, printer1_stdfile, printer1_autocutter, printer1_bgconnect, printer1_dummy, video1_avail, video1_conn, video1_channel, video1_version, feedisplay_avail, feedisplay_conn, feedisplay_paralel, feedisplay_version, bg_avail, bg_conn, bg_paralel, bg_value, sound_avail, sound_conn, sound_version, sound_partisi, id_pos, sizeable, pjg_lcd, video1_bright, video2_avail, video2_conn, video2_channel, video2_version, video2_bright, video2_sizeable, smartcard_avail, smartcard_speed, smartcard_port, printer2_avail, printer2_conn, printer2_spd, printer2_stdfile, printer2_autocutter, printer2_bgconnect, printer2_dummy, fan1_maxval, fan2_maxval, temp1_maxval, temp2_maxval, sensor_fan1, sensor_fan2, sensor_temp1, sensor_temp2, bg_type, bg_usb, video3_avail, video3_conn, video3_channel, video3_version, video3_bright, video3_sizeable) VALUES (1, '/dev/usb/lp0', '9600', 1, 1, 0, 0, 0, 'http://192.168.10.201:81/snapshot.cgi?user=admin&pwd=888888', 0, 0, 0, 'COM1', '0', 0, 0, 'COM1', 0, 85, 0, '/dev/dsp', 0, 0, '01', 0, 16, '', 0, '', 0, 0, '', 0, 1, 0, 'SERIAL:/dev/ttyUSB0', 0, '', '', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, NULL, 0, 0, '', 0, 0, '', 0);


--
-- TOC entry 2304 (class 0 OID 16463)
-- Dependencies: 152
-- Data for Name: customer; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2305 (class 0 OID 16470)
-- Dependencies: 153
-- Data for Name: detail_customer; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2306 (class 0 OID 16476)
-- Dependencies: 154
-- Data for Name: detail_langganan; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2307 (class 0 OID 16480)
-- Dependencies: 155
-- Data for Name: detail_langganan_next; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO detail_langganan_next (id_langganan, nopol, jenis, akses, enable) VALUES ('0120/MEM/09/2007', 'B2310MY', 'A', NULL, 1);
INSERT INTO detail_langganan_next (id_langganan, nopol, jenis, akses, enable) VALUES ('0157/MEM/09/2007', 'B8483HY', 'C', NULL, 1);
INSERT INTO detail_langganan_next (id_langganan, nopol, jenis, akses, enable) VALUES ('0158/MEM/09/2007', 'B6761YJ', 'C', NULL, 1);
INSERT INTO detail_langganan_next (id_langganan, nopol, jenis, akses, enable) VALUES ('0200/MEM/09/2007', 'B2239OI', 'A', NULL, 1);
INSERT INTO detail_langganan_next (id_langganan, nopol, jenis, akses, enable) VALUES ('0203/MEM/09/2007', 'B6389KAQ', 'C', NULL, 1);


--
-- TOC entry 2308 (class 0 OID 16484)
-- Dependencies: 156
-- Data for Name: detail_pendaftaran; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2309 (class 0 OID 16487)
-- Dependencies: 157
-- Data for Name: detail_transaksi_parkir; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2310 (class 0 OID 16490)
-- Dependencies: 158
-- Data for Name: detail_transaksi_pulsa; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2311 (class 0 OID 16493)
-- Dependencies: 159
-- Data for Name: detail_transaksi_stiker; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2312 (class 0 OID 16500)
-- Dependencies: 160
-- Data for Name: detailpolajamkerja; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO detailpolajamkerja (hari, masuk, lama, efektif, keterangan, idpola, imasuk, ilama) VALUES (1, '2009-04-01 06:50:00', 480, 1, 'P,01', '006', NULL, NULL);
INSERT INTO detailpolajamkerja (hari, masuk, lama, efektif, keterangan, idpola, imasuk, ilama) VALUES (1, '2009-04-02 06:50:00', 480, 1, 'P,01', '006', NULL, NULL);
INSERT INTO detailpolajamkerja (hari, masuk, lama, efektif, keterangan, idpola, imasuk, ilama) VALUES (1, '2009-04-03 06:50:00', 480, 1, 'P,01', '006', NULL, NULL);
INSERT INTO detailpolajamkerja (hari, masuk, lama, efektif, keterangan, idpola, imasuk, ilama) VALUES (1, '2009-04-01 06:50:00', 480, 1, 'P,01', '007', NULL, NULL);
INSERT INTO detailpolajamkerja (hari, masuk, lama, efektif, keterangan, idpola, imasuk, ilama) VALUES (1, '2009-04-02 06:50:00', 480, 1, 'P,01', '007', NULL, NULL);
INSERT INTO detailpolajamkerja (hari, masuk, lama, efektif, keterangan, idpola, imasuk, ilama) VALUES (1, '2009-04-03 06:50:00', 480, 1, 'P,01', '007', NULL, NULL);
INSERT INTO detailpolajamkerja (hari, masuk, lama, efektif, keterangan, idpola, imasuk, ilama) VALUES (1, '2009-04-01 06:50:00', 480, 1, 'P,PK1', '008', NULL, NULL);
INSERT INTO detailpolajamkerja (hari, masuk, lama, efektif, keterangan, idpola, imasuk, ilama) VALUES (1, '2009-04-02 06:50:00', 480, 1, 'P,PK1', '008', NULL, NULL);
INSERT INTO detailpolajamkerja (hari, masuk, lama, efektif, keterangan, idpola, imasuk, ilama) VALUES (1, '2009-04-03 06:50:00', 480, 1, 'P,PK1', '008', NULL, NULL);
INSERT INTO detailpolajamkerja (hari, masuk, lama, efektif, keterangan, idpola, imasuk, ilama) VALUES (1, '2009-06-01 06:50:00', 480, 1, 'P,01', '00001', NULL, NULL);
INSERT INTO detailpolajamkerja (hari, masuk, lama, efektif, keterangan, idpola, imasuk, ilama) VALUES (1, '2009-06-02 14:50:00', 420, 1, 'S,01', '00001', NULL, NULL);


--
-- TOC entry 2313 (class 0 OID 16503)
-- Dependencies: 161
-- Data for Name: fingerlist; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2314 (class 0 OID 16509)
-- Dependencies: 162
-- Data for Name: foc; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO foc (notrans, id_langganan, nama, tanggal) VALUES (NULL, 'RSUD SALEWANGANG MAROS', '$D2AB1F86', 'OUMKVH8ZMG.');


--
-- TOC entry 2315 (class 0 OID 16515)
-- Dependencies: 163
-- Data for Name: freepass; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2316 (class 0 OID 16521)
-- Dependencies: 164
-- Data for Name: freepass_activation_log; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2317 (class 0 OID 16524)
-- Dependencies: 165
-- Data for Name: hari_libur; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2318 (class 0 OID 16527)
-- Dependencies: 166
-- Data for Name: indexnum; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO indexnum (kode, nama, value) VALUES ('0001', 'transaksi', '1');
INSERT INTO indexnum (kode, nama, value) VALUES ('0002', 'langganan', '1');
INSERT INTO indexnum (kode, nama, value) VALUES ('003', 'setoran', '1');
INSERT INTO indexnum (kode, nama, value) VALUES ('002', 'pesan', '1');
INSERT INTO indexnum (kode, nama, value) VALUES ('002', 'pesan', '1');
INSERT INTO indexnum (kode, nama, value) VALUES ('019', 'identitas', '1144');
INSERT INTO indexnum (kode, nama, value) VALUES ('025', 'sticker', '1144');


--
-- TOC entry 2319 (class 0 OID 16531)
-- Dependencies: 167
-- Data for Name: jenis_langganan; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO jenis_langganan (id, nama, bayar, tarif, periode_awal, masa_berlaku, maks, jenis_mobil) VALUES ('01', 'TENANT', 1, NULL, NULL, NULL, NULL, NULL);
INSERT INTO jenis_langganan (id, nama, bayar, tarif, periode_awal, masa_berlaku, maks, jenis_mobil) VALUES ('02', 'VIP/COMPLIMENT', 0, NULL, NULL, NULL, NULL, NULL);


--
-- TOC entry 2320 (class 0 OID 16537)
-- Dependencies: 168
-- Data for Name: jenis_mobil; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO jenis_mobil (id, nama, tanggal, short_cut, orang, validasi, need_access) VALUES ('A', 'Mobil', '2012-01-19 19:49:38.671', 'A', 0, 0, NULL);
INSERT INTO jenis_mobil (id, nama, tanggal, short_cut, orang, validasi, need_access) VALUES ('D', 'Truck/Box', '2012-01-19 19:49:48.203', 'D', 0, 0, NULL);
INSERT INTO jenis_mobil (id, nama, tanggal, short_cut, orang, validasi, need_access) VALUES ('C', 'Motor', '2018-03-23 18:18:03.312', 'C', 0, 0, 0);


--
-- TOC entry 2321 (class 0 OID 16542)
-- Dependencies: 169
-- Data for Name: keyallow; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO keyallow (idkey, keycode, reg_date) VALUES ('RSUD SALEWANGANG MAROS', '$D2AB1F86', 'MTcvMDcvMjAxOQ==');


--
-- TOC entry 2322 (class 0 OID 16548)
-- Dependencies: 170
-- Data for Name: kodeform; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO kodeform (kode, nama) VALUES (10013, 'Administrasi Data Parkir');
INSERT INTO kodeform (kode, nama) VALUES (10015, 'Administrasi Pelanggan');
INSERT INTO kodeform (kode, nama) VALUES (10016, 'Cetak Ulang Struk');
INSERT INTO kodeform (kode, nama) VALUES (10017, 'Config Setting');
INSERT INTO kodeform (kode, nama) VALUES (10018, 'Cetak Pendapatan');


--
-- TOC entry 2323 (class 0 OID 16551)
-- Dependencies: 171
-- Data for Name: konsolidasi; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2324 (class 0 OID 16554)
-- Dependencies: 172
-- Data for Name: kredit; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2325 (class 0 OID 16558)
-- Dependencies: 173
-- Data for Name: langganan; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2326 (class 0 OID 16566)
-- Dependencies: 174
-- Data for Name: langganan_next; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2327 (class 0 OID 16574)
-- Dependencies: 175
-- Data for Name: langganan_res; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2328 (class 0 OID 16582)
-- Dependencies: 176
-- Data for Name: level_user; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO level_user (level_id, level_code, level_name, create_by, create_date, update_by, update_date) VALUES (1, '0001', 'Administrator', '', '2009-06-22 14:09:01.297662', NULL, NULL);
INSERT INTO level_user (level_id, level_code, level_name, create_by, create_date, update_by, update_date) VALUES (4, '0003', 'Supervisor', '00001', '2009-07-14 14:23:00.433939', NULL, NULL);
INSERT INTO level_user (level_id, level_code, level_name, create_by, create_date, update_by, update_date) VALUES (2, '0005', 'Cashier', '', '2009-06-22 14:10:28.611146', 2, '2010-03-06 09:29:01.071891');
INSERT INTO level_user (level_id, level_code, level_name, create_by, create_date, update_by, update_date) VALUES (3, '0002', 'Leader', '00001', '2009-07-06 11:18:37.889806', 1, '2010-05-16 11:17:02.353611');


--
-- TOC entry 2329 (class 0 OID 16589)
-- Dependencies: 177
-- Data for Name: login_log; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'SS', '2012-06-04 14:32:22.203', '2012-06-04 14:34:37.203', '2012-06-04 14:32:22.203', 'ADMIN', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'SS', '2012-06-04 14:35:20.75', '2012-06-04 14:35:34.89', '2012-06-04 14:35:20.75', 'ADMIN', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'SS', '2012-06-04 14:35:38.937', '2012-06-04 14:36:57.109', '2012-06-04 14:35:38.937', 'ADMIN', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'SS', '2014-05-21 10:41:53.981067', '2014-05-21 12:54:18', '2014-05-21 10:41:53.981067', 'ADMIN', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'S1', '2014-05-21 12:53:13', '2014-05-21 12:54:18', '2014-05-21 12:53:14.225033', 'PK1', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'S1', '2014-05-21 12:55:42', '2014-05-21 12:58:47', '2014-05-21 12:55:43.695936', 'PK1', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'S1', '2014-05-21 13:07:36', '2014-05-21 13:10:57', '2014-05-21 13:07:37.669937', 'PK1', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'S1', '2014-05-21 13:10:10', '2014-05-21 13:10:57', '2014-05-21 13:10:11.102767', 'PK1', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'S1', '2014-05-21 13:11:15', '2014-05-21 13:16:57', '2014-05-21 13:11:16.897389', 'PK1', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'S1', '2014-05-21 13:17:03', '2014-05-21 13:17:45', '2014-05-21 13:17:05.058463', 'PK1', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'S1', '2014-05-21 13:17:49', '2014-05-21 13:17:59', '2014-05-21 13:17:50.557071', 'PK1', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'S1', '2014-05-21 13:18:47', '2014-05-21 13:30:50', '2014-05-21 13:19:08.618809', 'PK1', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'S1', '2014-05-21 13:19:12', '2014-05-21 13:30:50', '2014-05-21 13:19:13.304737', 'PK1', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'S1', '2014-05-21 13:21:39', '2014-05-21 13:30:50', '2014-05-21 13:21:40.76881', 'PK1', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'S1', '2014-05-21 13:28:25', '2014-05-21 13:30:50', '2014-05-21 13:28:26.100415', 'PK1', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'S1', '2014-05-21 13:31:15', '2014-05-21 13:47:29', '2014-05-21 13:31:16.595146', 'PK1', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'S1', '2014-05-21 13:34:09', '2014-05-21 13:47:29', '2014-05-21 13:34:10.558505', 'PK1', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'S1', '2014-05-21 13:38:57', '2014-05-21 13:47:29', '2014-05-21 13:40:16.821131', 'PK1', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'S1', '2014-05-21 13:40:20', '2014-05-21 13:47:29', '2014-05-21 13:40:22.032425', 'PK1', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'S2', '2014-05-21 13:47:16', '2014-05-21 13:47:29', '2014-05-21 13:47:16.741459', 'PK1', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'S2', '2014-05-21 13:48:18', '2014-05-21 13:48:30', '2014-05-21 13:48:20.277433', 'PK1', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'S2', '2014-05-21 14:16:52', '2014-05-21 14:21:30', '2014-05-21 14:17:35.435477', 'PK1', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'S2', '2014-05-21 14:17:39', '2014-05-21 14:21:30', '2014-05-21 14:21:04.437497', 'PK1', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'S2', '2014-05-21 14:21:11', '2014-05-21 14:21:30', '2014-05-21 14:21:25.537693', 'PK1', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'S2', '2014-05-21 14:23:05', '2014-05-21 14:44:16', '2014-05-21 14:23:46.960255', 'PK1', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'S2', '2014-05-21 14:24:03', '2014-05-21 14:44:16', '2014-05-21 14:24:08.091674', 'PK1', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'S2', '2014-05-21 14:24:34', '2014-05-21 14:44:16', '2014-05-21 14:24:35.588642', 'PK1', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'S2', '2014-05-21 14:28:25', '2014-05-21 14:44:16', '2014-05-21 14:28:26.113309', 'PK1', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'S2', '2014-05-21 14:31:39', '2014-05-21 14:44:16', '2014-05-21 14:31:41.309935', 'PK1', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'S2', '2014-05-21 14:32:45', '2014-05-21 14:44:16', '2014-05-21 14:32:46.744477', 'PK1', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'S2', '2014-05-21 14:34:00', '2014-05-21 14:44:16', '2014-05-21 14:34:01.226069', 'PK1', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'S2', '2014-05-21 14:35:42', '2014-05-21 14:44:16', '2014-05-21 14:35:43.644857', 'PK1', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'S2', '2014-05-21 14:37:06', '2014-05-21 14:44:16', '2014-05-21 14:37:07.361078', 'PK1', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'S2', '2014-05-21 14:38:55', '2014-05-21 14:44:16', '2014-05-21 14:38:56.122527', 'PK1', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'S2', '2014-05-21 14:40:28', '2014-05-21 14:44:16', '2014-05-21 14:40:29.713229', 'PK1', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'S2', '2014-05-21 14:47:39', '2014-05-21 15:03:38', '2014-05-21 14:47:40.855523', 'PK1', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'S2', '2014-05-21 15:03:43', '2014-05-21 15:06:54', '2014-05-21 15:03:45.230642', 'PK1', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'SS', '2014-05-22 19:40:44.893537', '2014-05-22 19:41:21.393502', '2014-05-22 19:40:44.893537', 'ADMIN', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'SS', '2014-05-22 20:04:15.957532', '2014-05-22 20:05:14.822806', '2014-05-22 20:04:15.957532', 'ADMIN', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'SS', '2018-03-08 18:40:00.375', '2018-03-08 18:45:38.796', '2018-03-08 18:40:00.375', 'ADMIN', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'SS', '2018-03-23 18:15:30.406', '2018-03-23 18:22:58.046', '2018-03-23 18:15:30.406', 'ADMIN', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'SS', '2018-03-23 18:28:55.109', '2018-03-23 18:29:08.546', '2018-03-23 18:28:55.109', 'ADMIN', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'SS', '2018-03-23 21:26:45.515', '2018-03-23 21:28:55.062', '2018-03-23 21:26:45.515', 'ADMIN', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'SS', '2018-03-23 22:05:58.218', '2018-03-23 22:06:38.156', '2018-03-23 22:05:58.218', 'ADMIN', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'SS', '2018-03-23 22:07:34.921', '2018-03-23 22:07:51.89', '2018-03-23 22:07:34.921', 'ADMIN', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'SS', '2018-03-24 09:51:52.921', '2018-03-24 09:58:40.453', '2018-03-24 09:51:52.921', 'ADMIN', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'SS', '2018-03-25 19:11:13.781', '2018-03-25 19:17:34.468', '2018-03-25 19:11:13.781', 'ADMIN', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'SS', '2018-03-25 19:16:02.703', '2018-03-25 19:17:34.468', '2018-03-25 19:16:02.703', 'ADMIN', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'SS', '2018-03-26 12:11:23', '2018-03-26 12:15:56.468', '2018-03-26 12:11:23', 'ADMIN', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'SS', '2018-03-26 12:15:35.343', '2018-03-26 12:15:56.468', '2018-03-26 12:15:35.343', 'ADMIN', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'SS', '2018-03-27 09:14:20.593', '2018-03-27 09:33:30.39', '2018-03-27 09:14:20.593', 'ADMIN', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'SS', '2018-03-27 13:22:31.843', '2018-03-27 13:36:30.437', '2018-03-27 13:22:31.843', 'ADMIN', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'SS', '2018-05-24 10:13:38.282', '2018-05-24 10:13:59.248', '2018-05-24 10:13:38.282', 'ADMIN', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'SS', '2018-05-26 09:41:27.644', '2018-05-26 09:41:43.872', '2018-05-26 09:41:27.644', 'ADMIN', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'SS', '2018-05-26 09:50:00.394', '2018-05-26 09:50:31.647', '2018-05-26 09:50:00.394', 'ADMIN', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'SS', '2018-05-26 09:52:17.358', '2018-05-26 09:53:25.17', '2018-05-26 09:52:17.358', 'ADMIN', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'SS', '2018-05-26 09:53:30.33', '2018-05-26 09:53:41.571', '2018-05-26 09:53:30.33', 'ADMIN', NULL, NULL);
INSERT INTO login_log (id_petugas, id_shift, time_login, time_logout, tanggal, pos, akses_id, adm) VALUES ('00001', 'SS', '2018-05-26 10:05:02.328', '2018-05-26 10:08:44.522', '2018-05-26 10:05:02.328', 'ADMIN', NULL, NULL);


--
-- TOC entry 2330 (class 0 OID 16592)
-- Dependencies: 178
-- Data for Name: lot_parkir; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2331 (class 0 OID 16595)
-- Dependencies: 179
-- Data for Name: manualbot; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2332 (class 0 OID 16601)
-- Dependencies: 180
-- Data for Name: master_device; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2333 (class 0 OID 16604)
-- Dependencies: 181
-- Data for Name: master_lokasi; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2334 (class 0 OID 16607)
-- Dependencies: 182
-- Data for Name: menuavail; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO menuavail (kode, keterangan) VALUES ('1', 'Ganti Password');
INSERT INTO menuavail (kode, keterangan) VALUES ('100000', 'Setup');
INSERT INTO menuavail (kode, keterangan) VALUES ('100001', 'Master Nama Pos Parkir');
INSERT INTO menuavail (kode, keterangan) VALUES ('100003', 'Master Jenis Mobil');
INSERT INTO menuavail (kode, keterangan) VALUES ('100004', 'Master SHIFT');
INSERT INTO menuavail (kode, keterangan) VALUES ('100005', 'Local Config');
INSERT INTO menuavail (kode, keterangan) VALUES ('100006', 'Master Tarif Parkir');
INSERT INTO menuavail (kode, keterangan) VALUES ('100007', 'Master Index Parkir');
INSERT INTO menuavail (kode, keterangan) VALUES ('100009', 'Biodata Pegawai');
INSERT INTO menuavail (kode, keterangan) VALUES ('100010', 'Akses Control');
INSERT INTO menuavail (kode, keterangan) VALUES ('100017', 'Ploting Karyawan');
INSERT INTO menuavail (kode, keterangan) VALUES ('100018', 'Master Unit Kerja');
INSERT INTO menuavail (kode, keterangan) VALUES ('100019', 'Master Seri Voucher');
INSERT INTO menuavail (kode, keterangan) VALUES ('100021', 'Master Tarif Langganan');
INSERT INTO menuavail (kode, keterangan) VALUES ('100022', 'Master Jenis Langganan');
INSERT INTO menuavail (kode, keterangan) VALUES ('100030', 'Master Hari Libur');
INSERT INTO menuavail (kode, keterangan) VALUES ('2', 'Keluar');
INSERT INTO menuavail (kode, keterangan) VALUES ('200000', 'Operasional');
INSERT INTO menuavail (kode, keterangan) VALUES ('200001', 'Transaksi Parkir');
INSERT INTO menuavail (kode, keterangan) VALUES ('200002', 'Transaksi Stiker');
INSERT INTO menuavail (kode, keterangan) VALUES ('200003', 'Transaksi Pelanggan');
INSERT INTO menuavail (kode, keterangan) VALUES ('200004', 'Transaksi Voucher');
INSERT INTO menuavail (kode, keterangan) VALUES ('200007', 'Input Konsolidasi Parkir');
INSERT INTO menuavail (kode, keterangan) VALUES ('200008', 'Pesan Ke Pos');
INSERT INTO menuavail (kode, keterangan) VALUES ('200015', 'Daftar Buka Gate Manual');
INSERT INTO menuavail (kode, keterangan) VALUES ('200016', 'Pesan Dari Pos');
INSERT INTO menuavail (kode, keterangan) VALUES ('200017', 'Input Parkir Manual');
INSERT INTO menuavail (kode, keterangan) VALUES ('3', 'Keluar Program');
INSERT INTO menuavail (kode, keterangan) VALUES ('500000', 'Report');
INSERT INTO menuavail (kode, keterangan) VALUES ('500001', 'Transaksi Parkir');
INSERT INTO menuavail (kode, keterangan) VALUES ('500002', 'Transaksi Voucher');
INSERT INTO menuavail (kode, keterangan) VALUES ('500003', 'Transaksi Stiker');
INSERT INTO menuavail (kode, keterangan) VALUES ('500004', 'Transaksi Member/Pelanggan');
INSERT INTO menuavail (kode, keterangan) VALUES ('500005', 'Laporan Konsolidasi');
INSERT INTO menuavail (kode, keterangan) VALUES ('500008', 'Laporan Historikal Login');
INSERT INTO menuavail (kode, keterangan) VALUES ('500009', 'Laporan Pembatalan Transaksi');
INSERT INTO menuavail (kode, keterangan) VALUES ('500010', 'Monitor Kendaraan Di Dalam');
INSERT INTO menuavail (kode, keterangan) VALUES ('500011', 'Laporan Masalah Di Pos Keluar');
INSERT INTO menuavail (kode, keterangan) VALUES ('500014', 'Laporan Penghapusan VIP/Compliment');
INSERT INTO menuavail (kode, keterangan) VALUES ('500015', 'Laporan Perubahan Langganan');
INSERT INTO menuavail (kode, keterangan) VALUES ('500018', 'Koreksi Data Parkir (Cara Pembayaran)');
INSERT INTO menuavail (kode, keterangan) VALUES ('500110', 'Transaksi Per Pintu/pos');
INSERT INTO menuavail (kode, keterangan) VALUES ('500111', 'Transaksi Harian');
INSERT INTO menuavail (kode, keterangan) VALUES ('500112', 'Transaksi Bulanan');
INSERT INTO menuavail (kode, keterangan) VALUES ('500120', 'Laporan Detail Transaksi Harian');
INSERT INTO menuavail (kode, keterangan) VALUES ('500200', 'Transaksi By Shift');
INSERT INTO menuavail (kode, keterangan) VALUES ('500204', 'Laporan Detail Transaksi Harian');
INSERT INTO menuavail (kode, keterangan) VALUES ('500210', 'Transaksi Per Pintu/pos');
INSERT INTO menuavail (kode, keterangan) VALUES ('500211', 'Transaksi Harian');
INSERT INTO menuavail (kode, keterangan) VALUES ('500212', 'Transaksi Bulanan');
INSERT INTO menuavail (kode, keterangan) VALUES ('500217', 'Laporan Harian Pandapatan Parkir');
INSERT INTO menuavail (kode, keterangan) VALUES ('500224', 'Laporan Harian Pandapatan Parkir');
INSERT INTO menuavail (kode, keterangan) VALUES ('500230', 'Transaksi Bulanan');
INSERT INTO menuavail (kode, keterangan) VALUES ('500231', 'Transaksi Pengunjung Umum Bulanan');
INSERT INTO menuavail (kode, keterangan) VALUES ('500240', 'Transaksi Bulanan');
INSERT INTO menuavail (kode, keterangan) VALUES ('500241', 'Transaksi Pengunjung Umum Bulanan');
INSERT INTO menuavail (kode, keterangan) VALUES ('500242', 'Laporan Bulanan Pandapatan Parkir');
INSERT INTO menuavail (kode, keterangan) VALUES ('200022', 'Daftar Cetak Ulang Struk');
INSERT INTO menuavail (kode, keterangan) VALUES ('200023', 'Laporan Aktivitas transaksi Member');


--
-- TOC entry 2336 (class 0 OID 16633)
-- Dependencies: 187
-- Data for Name: nama_pos; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO nama_pos (id, nama, jenis, tanggal, lokasi, grace_period, manless, area, berlaku_maksimal) VALUES ('01', 'Pintu Masuk Mobil', 0, '2018-03-23 18:15:59.906', NULL, 1, 1, NULL, NULL);
INSERT INTO nama_pos (id, nama, jenis, tanggal, lokasi, grace_period, manless, area, berlaku_maksimal) VALUES ('02', 'Pintu Masuk Motor', 0, '2018-03-23 18:16:03.39', NULL, 1, 1, NULL, NULL);
INSERT INTO nama_pos (id, nama, jenis, tanggal, lokasi, grace_period, manless, area, berlaku_maksimal) VALUES ('PK2', 'Pintu Keluar Motor', 1, '2018-03-23 18:16:07.234', NULL, 1, 0, NULL, NULL);
INSERT INTO nama_pos (id, nama, jenis, tanggal, lokasi, grace_period, manless, area, berlaku_maksimal) VALUES ('PK1', 'Pintu Keluar Mobil', 1, '2018-03-23 18:16:10.89', NULL, 1, 0, NULL, NULL);


--
-- TOC entry 2337 (class 0 OID 16637)
-- Dependencies: 188
-- Data for Name: netlist; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO netlist (ip, nama, enable, jenis) VALUES ('192.168.10.140', 'LINUX COMPTER', 1, 2);


--
-- TOC entry 2338 (class 0 OID 16640)
-- Dependencies: 189
-- Data for Name: nodestatus; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2339 (class 0 OID 16643)
-- Dependencies: 190
-- Data for Name: nopolpool; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2340 (class 0 OID 16646)
-- Dependencies: 191
-- Data for Name: nx_audit; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO nx_audit (db, ratio, "real", audit, last, awal, akhir, limit_value) VALUES ('test', 100, 0, 0, '2018-03-09 21:25:47.859', NULL, NULL, 100000);


--
-- TOC entry 2342 (class 0 OID 16670)
-- Dependencies: 194
-- Data for Name: parkir_transaksi; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2343 (class 0 OID 16680)
-- Dependencies: 195
-- Data for Name: pass_dump; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2344 (class 0 OID 16683)
-- Dependencies: 196
-- Data for Name: pegawai; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO pegawai (nomer, nama, alamat, tgl_lahir, tgl_masuk, username, password, foto, bisalogin, status, jeniskelamin, agama, telepon, alamat_lahir, alamat_sekarang, nip, statusabsen, level_pegawai) VALUES ('00001', 'Administrator', '', '2004-02-25', '2004-02-25', 'admin', 'admin', NULL, 1, 1, 0, '0001', '', '', '', '', NULL, '0001');


--
-- TOC entry 2345 (class 0 OID 16689)
-- Dependencies: 197
-- Data for Name: pendaftaran; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2346 (class 0 OID 16692)
-- Dependencies: 198
-- Data for Name: pesan; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2347 (class 0 OID 16698)
-- Dependencies: 199
-- Data for Name: pulsa; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2348 (class 0 OID 16701)
-- Dependencies: 200
-- Data for Name: randomnumber; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO randomnumber (used, pos, number) VALUES (0, '01', '0001');
INSERT INTO randomnumber (used, pos, number) VALUES (0, '02', '0001');


--
-- TOC entry 2349 (class 0 OID 16707)
-- Dependencies: 201
-- Data for Name: reprint; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2350 (class 0 OID 16713)
-- Dependencies: 202
-- Data for Name: seri_freepas; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2351 (class 0 OID 16721)
-- Dependencies: 203
-- Data for Name: setoran; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO setoran (no_setoran, tgl_setoran, id_penyetor, shift, pintu, setoran_utk_tgl, jml_uang, jml_vaucher, id_penerima, admin, jml_masalah, jml_masalah_nilai) VALUES ('0001/STR/09/2007', '2007-09-08 00:00:00', '14', 'S1', 'PK2', '2007-09-08 00:00:00', 342500, 0, '14', '03', NULL, NULL);
INSERT INTO setoran (no_setoran, tgl_setoran, id_penyetor, shift, pintu, setoran_utk_tgl, jml_uang, jml_vaucher, id_penerima, admin, jml_masalah, jml_masalah_nilai) VALUES ('0002/STR/09/2007', '2007-09-08 00:00:00', '15', 'S1', 'PK1', '2007-09-08 00:00:00', 667000, 0, '14', '03', NULL, NULL);
INSERT INTO setoran (no_setoran, tgl_setoran, id_penyetor, shift, pintu, setoran_utk_tgl, jml_uang, jml_vaucher, id_penerima, admin, jml_masalah, jml_masalah_nilai) VALUES ('0003/STR/09/2007', '2007-09-16 00:00:00', '15', 'S1', 'PK2', '2007-09-16 00:00:00', 142500, 0, '15', '00001', NULL, NULL);
INSERT INTO setoran (no_setoran, tgl_setoran, id_penyetor, shift, pintu, setoran_utk_tgl, jml_uang, jml_vaucher, id_penerima, admin, jml_masalah, jml_masalah_nilai) VALUES ('0004/STR/09/2007', '2007-09-16 00:00:00', '16', 'S1', 'PK1', '2007-09-16 00:00:00', 191000, 0, '15', '00001', NULL, NULL);


--
-- TOC entry 2352 (class 0 OID 16726)
-- Dependencies: 204
-- Data for Name: shift; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO shift (id, mulai, selama, tanggal) VALUES ('S2', '13:45', 480, '2009-09-12 06:16:24.21708');
INSERT INTO shift (id, mulai, selama, tanggal) VALUES ('S1', '05:45', 480, '2009-09-12 06:16:30.437507');
INSERT INTO shift (id, mulai, selama, tanggal) VALUES ('S3', '21:45', 540, '2009-09-12 06:17:07.674287');


--
-- TOC entry 2353 (class 0 OID 16747)
-- Dependencies: 209
-- Data for Name: softseting; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO softseting (namasoft, versoft, namasystem, versystem, namaperusahaan, alamat, telepon, namalokasi, alamatlokasi, softplatform, lisensi, period, tipesoft, banyakclient, logo, tanggal, parkintf, npwp, nppkp, smson, mail_name, mail_address, incom_mail, out_mail, pasw_mail, stok_awal, stok_kunci, cabang_lokasi) VALUES ('Parking System', '1.00', 'Parking System', '1.00', ' ', '-', '-', 'RSUD SALEWANGANG MAROS', '-', 0, 1, 30, 4, 0, 'OUMKVH8ZMG.', '2011-03-07 19:21:42.734', NULL, '-', '-', 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);


--
-- TOC entry 2354 (class 0 OID 16754)
-- Dependencies: 210
-- Data for Name: stasiunkerja; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO stasiunkerja (kode, nama, margin, spv, target, contact, alamat, alamat1, alamat2, tntcd, rntno) VALUES ('02', 'Langganan', 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);


--
-- TOC entry 2355 (class 0 OID 16761)
-- Dependencies: 211
-- Data for Name: stok_barcode; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2356 (class 0 OID 16767)
-- Dependencies: 212
-- Data for Name: stokkartu; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2357 (class 0 OID 16770)
-- Dependencies: 213
-- Data for Name: tarif; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO tarif (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, tarif_inap, batas_min_inap, max_kena_charge, tarif_member, tarif_voucher, voucher_frek, voucher_time, voucher_base, voucher_base_time, asuransi_incl, denda_only_casual, frek_interval, frek_waktu2, free_for_validasi, time_base_maks, free_pos_default, tarif_valet, type_tarif_member, start_time_member_charge, stop_time_member_charge, min_time_tarif_member, batas_inap_min, periode_inap, free_same_day, valet_extra_time, extra_charge_value, extra_charge_time, tarif3, waktu3, frek_waktu3, denda_member, denda_only, gratis_waktu_tertentu, start_gratis_waktu_tertentu, stop_gratis_waktu_tertentu, tarif_member_valid_pos, free_same_hour, max_free_same_hour) VALUES ('B', 0, 0, 0, 60, 0, 0, 0, 0, '2005-03-18 15:25:29.830271', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO tarif (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, tarif_inap, batas_min_inap, max_kena_charge, tarif_member, tarif_voucher, voucher_frek, voucher_time, voucher_base, voucher_base_time, asuransi_incl, denda_only_casual, frek_interval, frek_waktu2, free_for_validasi, time_base_maks, free_pos_default, tarif_valet, type_tarif_member, start_time_member_charge, stop_time_member_charge, min_time_tarif_member, batas_inap_min, periode_inap, free_same_day, valet_extra_time, extra_charge_value, extra_charge_time, tarif3, waktu3, frek_waktu3, denda_member, denda_only, gratis_waktu_tertentu, start_gratis_waktu_tertentu, stop_gratis_waktu_tertentu, tarif_member_valid_pos, free_same_hour, max_free_same_hour) VALUES ('S', 1000, 1000, 60, 60, 0, 0, 10000, 0, '2009-09-08 11:24:41.91083', 0, 0, 2000, 0, 0, 0, 0, '  :  :  ', '  :  :  ', 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO tarif (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, tarif_inap, batas_min_inap, max_kena_charge, tarif_member, tarif_voucher, voucher_frek, voucher_time, voucher_base, voucher_base_time, asuransi_incl, denda_only_casual, frek_interval, frek_waktu2, free_for_validasi, time_base_maks, free_pos_default, tarif_valet, type_tarif_member, start_time_member_charge, stop_time_member_charge, min_time_tarif_member, batas_inap_min, periode_inap, free_same_day, valet_extra_time, extra_charge_value, extra_charge_time, tarif3, waktu3, frek_waktu3, denda_member, denda_only, gratis_waktu_tertentu, start_gratis_waktu_tertentu, stop_gratis_waktu_tertentu, tarif_member_valid_pos, free_same_hour, max_free_same_hour) VALUES ('M', 2000, 2000, 60, 60, 5, 0, 20000, 0, '2010-02-25 15:47:49.427876', 0, 0, 0, 0, 0, 0, 0, '  :  :  ', '  :  :  ', 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO tarif (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, tarif_inap, batas_min_inap, max_kena_charge, tarif_member, tarif_voucher, voucher_frek, voucher_time, voucher_base, voucher_base_time, asuransi_incl, denda_only_casual, frek_interval, frek_waktu2, free_for_validasi, time_base_maks, free_pos_default, tarif_valet, type_tarif_member, start_time_member_charge, stop_time_member_charge, min_time_tarif_member, batas_inap_min, periode_inap, free_same_day, valet_extra_time, extra_charge_value, extra_charge_time, tarif3, waktu3, frek_waktu3, denda_member, denda_only, gratis_waktu_tertentu, start_gratis_waktu_tertentu, stop_gratis_waktu_tertentu, tarif_member_valid_pos, free_same_hour, max_free_same_hour) VALUES ('T', 2000, 2000, 60, 60, 30, 0, 20000, 0, '2010-02-25 15:48:30.630806', 2000, 0, 0, 0, 0, 0, 0, '  :  :  ', '  :  :  ', 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO tarif (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, tarif_inap, batas_min_inap, max_kena_charge, tarif_member, tarif_voucher, voucher_frek, voucher_time, voucher_base, voucher_base_time, asuransi_incl, denda_only_casual, frek_interval, frek_waktu2, free_for_validasi, time_base_maks, free_pos_default, tarif_valet, type_tarif_member, start_time_member_charge, stop_time_member_charge, min_time_tarif_member, batas_inap_min, periode_inap, free_same_day, valet_extra_time, extra_charge_value, extra_charge_time, tarif3, waktu3, frek_waktu3, denda_member, denda_only, gratis_waktu_tertentu, start_gratis_waktu_tertentu, stop_gratis_waktu_tertentu, tarif_member_valid_pos, free_same_hour, max_free_same_hour) VALUES ('E', 1000, 1500, 60, 60, 6, 0, 10000, 4500, '2009-01-17 13:43:35.707369', 0, 0, 0, 0, 0, 1, 0, '  :  :  ', '  :  :  ', 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO tarif (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, tarif_inap, batas_min_inap, max_kena_charge, tarif_member, tarif_voucher, voucher_frek, voucher_time, voucher_base, voucher_base_time, asuransi_incl, denda_only_casual, frek_interval, frek_waktu2, free_for_validasi, time_base_maks, free_pos_default, tarif_valet, type_tarif_member, start_time_member_charge, stop_time_member_charge, min_time_tarif_member, batas_inap_min, periode_inap, free_same_day, valet_extra_time, extra_charge_value, extra_charge_time, tarif3, waktu3, frek_waktu3, denda_member, denda_only, gratis_waktu_tertentu, start_gratis_waktu_tertentu, stop_gratis_waktu_tertentu, tarif_member_valid_pos, free_same_hour, max_free_same_hour) VALUES ('A', 2000, 3000, 60, 60, 0, 0, 15000, 25000, '2018-03-23 21:27:33.343', 0, 0, 0, 0, 0, 1, 0, '  :  :  ', '  :  :  ', 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 24, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, 0, 0, 0, '  :  ', '  :  ', NULL, NULL, NULL);
INSERT INTO tarif (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, tarif_inap, batas_min_inap, max_kena_charge, tarif_member, tarif_voucher, voucher_frek, voucher_time, voucher_base, voucher_base_time, asuransi_incl, denda_only_casual, frek_interval, frek_waktu2, free_for_validasi, time_base_maks, free_pos_default, tarif_valet, type_tarif_member, start_time_member_charge, stop_time_member_charge, min_time_tarif_member, batas_inap_min, periode_inap, free_same_day, valet_extra_time, extra_charge_value, extra_charge_time, tarif3, waktu3, frek_waktu3, denda_member, denda_only, gratis_waktu_tertentu, start_gratis_waktu_tertentu, stop_gratis_waktu_tertentu, tarif_member_valid_pos, free_same_hour, max_free_same_hour) VALUES ('C', 1000, 2000, 60, 60, 0, 0, 10000, 15000, '2018-03-23 21:28:11.578', 0, 0, 0, 0, 0, 1, 0, '  :  :  ', '  :  :  ', 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 24, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, 0, 0, 0, '  :  ', '  :  ', NULL, NULL, NULL);
INSERT INTO tarif (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, tarif_inap, batas_min_inap, max_kena_charge, tarif_member, tarif_voucher, voucher_frek, voucher_time, voucher_base, voucher_base_time, asuransi_incl, denda_only_casual, frek_interval, frek_waktu2, free_for_validasi, time_base_maks, free_pos_default, tarif_valet, type_tarif_member, start_time_member_charge, stop_time_member_charge, min_time_tarif_member, batas_inap_min, periode_inap, free_same_day, valet_extra_time, extra_charge_value, extra_charge_time, tarif3, waktu3, frek_waktu3, denda_member, denda_only, gratis_waktu_tertentu, start_gratis_waktu_tertentu, stop_gratis_waktu_tertentu, tarif_member_valid_pos, free_same_hour, max_free_same_hour) VALUES ('D', 5000, 5000, 60, 60, 0, 0, 20000, 35000, '2018-03-23 21:28:48.859', 0, 0, 0, 0, 0, 1, 0, '  :  :  ', '  :  :  ', 0, 0, 0, 3, 0, 0, 0, 0, 1, 1, 0, 24, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, NULL, 0, 0, 0, '  :  ', '  :  ', NULL, NULL, NULL);


--
-- TOC entry 2358 (class 0 OID 16780)
-- Dependencies: 214
-- Data for Name: tarif_inap; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2359 (class 0 OID 16783)
-- Dependencies: 215
-- Data for Name: tarif_member; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2360 (class 0 OID 16786)
-- Dependencies: 216
-- Data for Name: tarif_rest; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1500, 2000, 60, 60, 0, 0, 20000, 1000000, '2007-09-01 10:12:06.75484', 1500, 60, 0, 0, NULL, NULL, 'Administrator', NULL, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('C', 1000, 0, 0, 120, 0, 0, 5000, 100000, '2007-09-01 10:12:59.893574', 0, 0, 0, 0, NULL, NULL, 'Administrator', NULL, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('D', 1500, 2000, 60, 60, 0, 0, 10000, 1000000, '2007-09-01 10:13:35.806216', 1500, 60, 0, 0, NULL, NULL, 'Administrator', NULL, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('C', 500, 1000, 60, 60, 0, 0, 5000, 2500, '2007-09-01 10:34:32.920438', 0, 0, 0, 0, 0, 0, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 60, 0, 0, 10000, 4500, '2007-09-01 10:36:57.41347', 0, 0, 0, 0, 0, 0, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 60, 0, 0, 10000, 4500, '2007-09-01 10:44:51.50769', 0, 0, 0, 0, 0, 0, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('C', 500, 1000, 120, 60, 0, 0, 5000, 2500, '2007-09-05 11:51:51.74688', 0, 0, 0, 0, 0, 0, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('C', 500, 1000, 120, 60, 0, 0, 5000, 2500, '2007-09-06 11:39:16.299393', 0, 0, 0, 0, 0, 0, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('E', 0, 2000, 60, 0, 15, 0, 0, 4500, '2007-09-07 18:15:51.304166', 1500, 60, 0, 0, 0, 0, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('E', 1000, 1500, 60, 60, 15, 0, 0, 4500, '2007-09-07 18:16:22.63062', 0, 0, 0, 0, 0, 0, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 60, 0, 0, 10000, 4500, '2007-12-11 13:45:11.459611', 0, 0, 0, 0, 0, 0, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('D', 1000, 1500, 60, 60, 0, 0, 10000, 4500, '2007-12-11 13:47:07.916932', 0, 0, 0, 0, 0, 0, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('D', 1000, 1500, 60, 60, 6, 0, 10000, 4500, '2007-12-11 13:47:59.532854', 0, 0, 0, 0, 0, 0, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 60, 6, 0, 10000, 4500, '2007-12-11 13:48:09.301763', 0, 0, 0, 0, 0, 0, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 60, 0, 0, 10000, 4500, '2007-12-11 14:40:19.807957', 0, 0, 0, 0, 0, 0, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('D', 1000, 1500, 60, 60, 0, 0, 10000, 4500, '2007-12-11 14:40:42.458525', 0, 0, 0, 0, 0, 0, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('E', 1000, 1500, 60, 60, 15, 0, 10000, 4500, '2007-12-11 14:41:17.927232', 0, 0, 0, 0, 0, 0, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 60, 6, 0, 10000, 4500, '2008-02-22 11:31:19.043921', 0, 0, 0, 0, 0, 0, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('C', 500, 1000, 120, 60, 0, 0, 5000, 2500, '2008-02-22 11:33:46.903536', 0, 0, 0, 0, 0, 0, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('E', 1000, 1500, 60, 60, 6, 0, 10000, 4500, '2008-02-22 13:01:20.787082', 0, 0, 0, 0, 0, 0, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 60, 5, 0, 10000, 4500, '2008-03-01 14:49:55.700518', 0, 0, 0, 0, 0, 0, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('E', 1000, 1500, 60, 60, 5, 0, 10000, 4500, '2008-03-01 14:50:20.731955', 0, 0, 0, 0, 0, 0, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 60, 6, 0, 10000, 4500, '2008-03-24 11:30:32.536263', 0, 0, 0, 0, 0, 0, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 60, 5, 0, 10000, 4500, '2008-04-01 07:53:17.93908', 0, 0, 0, 0, 0, 0, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 60, 6, 0, 10000, 4500, '2008-04-28 09:18:05.80089', 0, 0, 0, 0, 0, 0, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 60, 6, 0, 10000, 4500, '2008-05-22 13:55:58.902896', 0, 0, 0, 0, 0, 0, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 60, 5, 0, 10000, 4500, '2008-05-24 13:16:39.521487', 0, 0, 0, 0, 0, 0, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 60, 6, 0, 10000, 4500, '2008-06-05 12:58:11.578819', 0, 0, 0, 0, 0, 0, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 60, 5, 0, 10000, 4500, '2008-06-06 11:23:47.558075', 0, 0, 0, 0, 0, 0, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 60, 6, 0, 10000, 4500, '2008-06-07 12:11:11.832919', 0, 0, 0, 0, 0, 0, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 60, 5, 0, 10000, 4500, '2008-06-18 11:24:24.530934', 0, 0, 0, 0, 0, 0, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('C', 500, 1000, 120, 60, 0, 0, 5000, 2500, '2008-06-18 11:24:39.513487', 0, 0, 0, 0, 0, 0, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('D', 1000, 1500, 60, 60, 6, 0, 10000, 4500, '2008-06-18 11:24:49.11809', 0, 0, 0, 0, 0, 0, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('E', 1000, 1500, 60, 60, 6, 0, 10000, 4500, '2008-06-18 11:24:59.824413', 0, 0, 0, 0, 0, 0, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 60, 5, 0, 10000, 4500, '2008-06-18 11:31:56.729792', 0, 0, 0, 0, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 60, 5, 0, 10000, 4500, '2008-06-18 12:38:03.860449', 0, 0, 0, 0, 0, 0, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('C', 500, 1000, 120, 60, 0, 0, 5000, 2500, '2008-06-18 12:38:14.340971', 0, 0, 0, 0, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('D', 1000, 1500, 60, 60, 6, 0, 10000, 4500, '2008-06-18 12:38:23.053293', 0, 0, 0, 0, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('E', 1000, 1500, 60, 60, 6, 0, 10000, 4500, '2008-06-18 12:38:30.764118', 0, 0, 0, 0, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 60, 5, 0, 10000, 4500, '2008-06-18 13:26:48.368272', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('C', 500, 1000, 120, 60, 0, 0, 5000, 2500, '2008-06-18 13:27:02.21023', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('D', 1000, 1500, 60, 60, 6, 0, 10000, 4500, '2008-06-18 13:27:12.505914', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('E', 1000, 1500, 60, 60, 6, 0, 10000, 4500, '2008-06-18 13:27:22.887346', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 60, 5, 0, 10000, 4500, '2008-06-18 14:57:21.849004', 0, 0, 0, 0, 0, 0, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 60, 5, 0, 10000, 4500, '2008-06-26 19:10:49.618118', 0, 0, 0, 0, 0, 0, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('C', 500, 1000, 120, 60, 0, 0, 5000, 2500, '2008-06-26 19:10:59.690638', 0, 0, 0, 0, 0, 0, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('D', 1000, 1500, 60, 60, 6, 0, 10000, 4500, '2008-06-26 19:11:08.161672', 0, 0, 0, 0, 0, 0, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('E', 1000, 1500, 60, 60, 6, 0, 10000, 4500, '2008-06-26 19:11:16.546499', 0, 0, 0, 0, 0, 0, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 60, 5, 0, 10000, 4500, '2008-06-27 11:09:16.449972', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('D', 1000, 1500, 60, 60, 6, 0, 10000, 4500, '2008-06-27 11:09:27.038896', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('E', 1000, 1500, 60, 60, 6, 0, 10000, 4500, '2008-06-27 11:09:43.087008', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('E', 1000, 1500, 60, 60, 4, 0, 10000, 4500, '2008-07-09 07:21:50.937722', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('E', 1000, 1500, 60, 60, 6, 0, 10000, 4500, '2008-07-09 07:21:56.641471', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('D', 1000, 1500, 60, 60, 4, 0, 10000, 4500, '2008-07-09 07:22:36.199962', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('D', 1000, 1500, 60, 60, 5, 0, 10000, 4500, '2008-07-09 11:27:20.950874', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 60, 4, 0, 10000, 4500, '2008-07-09 11:27:38.643794', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('D', 1000, 1500, 60, 60, 4, 0, 10000, 4500, '2008-07-29 15:38:14.784009', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('D', 1000, 1500, 60, 60, 4, 0, 10000, 4500, '2008-07-29 15:38:48.412709', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('E', 1000, 1500, 60, 60, 5, 0, 10000, 4500, '2008-11-11 10:49:03.157769', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 60, 4, 0, 10000, 4500, '2008-11-15 11:52:47.265723', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('D', 1000, 1500, 60, 60, 4, 0, 10000, 4500, '2008-11-15 11:52:58.543496', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 60, 3, 0, 10000, 4500, '2008-11-16 09:00:29.813417', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 60, 4, 0, 10000, 4500, '2008-11-16 10:07:23.907045', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('D', 1000, 1500, 60, 60, 3, 0, 10000, 4500, '2008-11-17 11:54:28.878988', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('E', 1000, 1500, 60, 60, 4, 0, 10000, 4500, '2008-11-18 12:21:17.633429', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 60, 5, 0, 10000, 4500, '2008-11-19 12:37:15.334931', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 60, 4, 0, 10000, 4500, '2008-11-22 11:11:35.203862', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 60, 4, 0, 10000, 4500, '2008-12-27 10:25:42.923615', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('D', 1000, 1500, 60, 60, 4, 0, 10000, 4500, '2008-12-27 10:26:01.640066', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('C', 500, 1000, 120, 60, 0, 0, 5000, 2500, '2008-12-27 10:26:39.604232', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 60, 3, 0, 10000, 4500, '2008-12-27 10:28:09.437085', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 30, 3, 0, 10000, 4500, '2008-12-27 10:28:21.560633', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('C', 500, 1000, 120, 60, 0, 0, 5000, 2500, '2008-12-27 10:28:54.603528', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('D', 1000, 1500, 60, 60, 3, 0, 10000, 4500, '2008-12-27 10:29:13.288691', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 30, 3, 0, 10000, 4500, '2008-12-27 10:34:16.605304', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('C', 500, 1000, 120, 45, 0, 0, 5000, 2500, '2008-12-27 10:34:45.145465', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('D', 1000, 1500, 60, 30, 3, 0, 10000, 4500, '2008-12-27 10:35:01.928523', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 50, 3, 0, 10000, 4500, '2008-12-30 09:25:35.022435', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('D', 1000, 1500, 60, 50, 3, 0, 10000, 4500, '2008-12-30 09:26:08.596404', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('E', 1000, 1500, 60, 60, 5, 0, 10000, 4500, '2008-12-30 09:26:20.594973', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 30, 3, 0, 10000, 4500, '2008-12-30 16:38:34.111956', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('D', 1000, 1500, 60, 30, 3, 0, 10000, 4500, '2008-12-30 16:38:46.297896', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 55, 3, 0, 10000, 4500, '2008-12-30 16:38:55.406234', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('D', 1000, 1500, 60, 55, 3, 0, 10000, 4500, '2008-12-30 16:39:04.124038', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('E', 1000, 1500, 60, 60, 4, 0, 10000, 4500, '2008-12-30 16:39:11.951191', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('C', 500, 1000, 120, 30, 0, 0, 5000, 2500, '2008-12-30 16:39:23.62165', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 55, 4, 0, 10000, 4500, '2009-01-03 11:20:14.181166', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('C', 500, 1000, 120, 45, 0, 0, 5000, 2500, '2009-01-03 11:20:24.867356', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 40, 4, 0, 10000, 4500, '2009-01-03 16:47:27.096414', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('C', 500, 1000, 120, 30, 0, 0, 5000, 2500, '2009-01-03 16:47:36.2434', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 55, 4, 0, 10000, 4500, '2009-01-08 13:03:07.948542', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 55, 4, 0, 10000, 4500, '2009-01-10 11:16:37.496902', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('D', 1000, 1500, 60, 55, 4, 0, 10000, 4500, '2009-01-10 11:16:47.868755', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('C', 500, 1000, 120, 55, 0, 0, 5000, 2500, '2009-01-10 11:16:57.026821', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 45, 4, 0, 10000, 4500, '2009-01-10 13:06:10.588388', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('C', 500, 1000, 120, 30, 0, 0, 5000, 2500, '2009-01-10 13:06:36.441924', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('D', 1000, 1500, 60, 50, 4, 0, 10000, 4500, '2009-01-10 13:06:47.350818', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 55, 4, 0, 10000, 4500, '2009-01-16 11:34:42.884238', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('C', 500, 1000, 120, 45, 0, 0, 5000, 2500, '2009-01-16 11:34:51.727582', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 50, 4, 0, 10000, 4500, '2009-01-17 12:11:31.40856', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('E', 1000, 1500, 60, 60, 5, 0, 10000, 4500, '2009-01-17 12:11:47.630716', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 45, 4, 0, 10000, 4500, '2009-01-17 13:43:00.26084', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('C', 500, 1000, 120, 30, 0, 0, 5000, 2500, '2009-01-17 13:43:09.324371', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('C', 500, 1000, 120, 50, 0, 0, 5000, 2500, '2009-01-17 13:43:15.731511', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('E', 1000, 1500, 60, 60, 4, 0, 10000, 4500, '2009-01-17 13:43:29.495923', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('E', 1000, 1500, 60, 60, 4, 0, 10000, 4500, '2009-01-17 13:43:35.707369', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 55, 4, 0, 10000, 4500, '2009-01-20 09:33:09.35628', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('C', 500, 1000, 120, 50, 0, 0, 5000, 2500, '2009-01-20 09:33:18.512283', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 50, 0, 0, 10000, 4500, '2009-04-14 13:51:49.742907', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 50, 6, 0, 10000, 4500, '2009-05-11 09:24:23.853326', 0, 0, 0, 1, 0, 1, 'Administrator', 0, 24);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 60, 6, 0, 10000, 4500, '2009-05-14 08:15:25.795151', 0, 0, 0, 1, 0, 1, 'Administrator', 0, 24);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 1000, 1500, 60, 60, 6, 0, 10000, 4500, '2009-06-09 14:55:32.603936', 0, 0, 0, 1, 0, 1, 'Administrator', 0, 24);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('C', 500, 1000, 120, 30, 0, 0, 5000, 2500, '2009-06-09 14:59:19.019172', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('M', 2000, 2000, 60, 60, 0, 0, 10000, 0, '2009-09-08 11:24:31.086043', 0, 0, 2000, 0, 0, 0, 'Lukman H.M. Hasan', 0, 0);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('S', 1000, 1000, 60, 60, 0, 0, 5000, 0, '2009-09-08 11:24:41.91083', 0, 0, 2000, 0, 0, 0, 'Lukman H.M. Hasan', 0, 0);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('M', 2000, 2000, 60, 60, 0, 0, 20000, 0, '2010-02-25 15:47:49.427876', 0, 0, 2000, 0, 0, 0, 'Eka Widyaningsih', 0, 0);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('T', 2000, 2000, 60, 60, 30, 0, 20000, 0, '2010-02-25 15:48:30.630806', 2000, 60, 0, 0, 0, 0, 'Eka Widyaningsih', 0, 0);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 2000, 2000, 60, 60, 0, 0, 10000, 0, '2011-03-07 19:33:20.328', 0, 0, 2000, 1, 0, 1, 'Administrator', 0, 0);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('C', 1000, 1000, 60, 60, 0, 0, 5000, 0, '2011-03-07 19:33:31.921', 0, 0, 1000, 1, 0, 1, 'Administrator', 0, 0);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('D', 1000, 1500, 60, 55, 0, 0, 10000, 4500, '2011-03-07 19:33:56.093', 0, 0, 0, 1, 0, 1, 'Administrator', 0, NULL);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('A', 2000, 2000, 60, 60, 0, 0, 10000, 0, '2018-03-23 21:27:33.343', 0, 0, 0, 0, 0, 0, 'Administrator', 0, 24);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('C', 1000, 1000, 60, 60, 0, 0, 5000, 0, '2018-03-23 21:28:11.578', 0, 0, 0, 0, 0, 0, 'Administrator', 0, 24);
INSERT INTO tarif_rest (id_mobil, tarif, tarif_interval, "interval", waktu_tarif, waktu_gratis, bayar_dimuka, denda, maksimum, tanggal, tarif2, waktu2, tarif_period, max_per_hari, min_per_hari, time_base, adm, tarif_inap, time_base_maks) VALUES ('D', 3000, 3000, 60, 60, 0, 0, 10000, 0, '2018-03-23 21:28:48.859', 0, 0, 0, 0, 0, 0, 'Administrator', 0, 24);


--
-- TOC entry 2361 (class 0 OID 16789)
-- Dependencies: 217
-- Data for Name: tarif_stiker; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2362 (class 0 OID 16795)
-- Dependencies: 218
-- Data for Name: tiket_masalah; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2363 (class 0 OID 16813)
-- Dependencies: 222
-- Data for Name: transaksi_gantiid; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2364 (class 0 OID 16816)
-- Dependencies: 223
-- Data for Name: transaksi_inap; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2365 (class 0 OID 16823)
-- Dependencies: 224
-- Data for Name: transaksi_masalah; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2341 (class 0 OID 16652)
-- Dependencies: 192
-- Data for Name: transaksi_parkir; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO transaksi_parkir (id, no_pol, id_kendaraan, status, id_pintu_masuk, id_pintu_keluar, waktu_masuk, waktu_keluar, id_op_masuk, id_op_keluar, id_shift_masuk, id_shift_keluar, kategori, status_transaksi, bayar_masuk, bayar_keluar, jenis_system, tanggal, pic_body_masuk, pic_body_keluar, pic_driver_masuk, pic_driver_keluar, pic_no_pol_masuk, pic_no_pol_keluar, sinkron, adm, alasan, pmlogin, pklogin, upload, manual, veri_kode, veri_check, veri_adm, veri_date, denda, extra_bayar, no_barcode, jenis_langganan, post_pay, reff_kode, valet_adm, waktu_valet, valet_charge, valet_ops, valet_nopol, login_waktu_valet, cara_bayar, unit_member, reserved, casual_denda, no_voucher, seri_voucher, no_access_in, no_access_out, inap, pic_plat_masuk, pic_plat_keluar) VALUES ('010001', '0100012105141044', 'A', 1, '01', NULL, '2014-05-21 10:44:29', NULL, 'NO-OP', NULL, 'S1', NULL, NULL, '0', NULL, NULL, NULL, '2014-05-21 10:44:30.342832', '', NULL, '', NULL, NULL, NULL, 0, NULL, NULL, '2014-05-21 05:45:00', NULL, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO transaksi_parkir (id, no_pol, id_kendaraan, status, id_pintu_masuk, id_pintu_keluar, waktu_masuk, waktu_keluar, id_op_masuk, id_op_keluar, id_shift_masuk, id_shift_keluar, kategori, status_transaksi, bayar_masuk, bayar_keluar, jenis_system, tanggal, pic_body_masuk, pic_body_keluar, pic_driver_masuk, pic_driver_keluar, pic_no_pol_masuk, pic_no_pol_keluar, sinkron, adm, alasan, pmlogin, pklogin, upload, manual, veri_kode, veri_check, veri_adm, veri_date, denda, extra_bayar, no_barcode, jenis_langganan, post_pay, reff_kode, valet_adm, waktu_valet, valet_charge, valet_ops, valet_nopol, login_waktu_valet, cara_bayar, unit_member, reserved, casual_denda, no_voucher, seri_voucher, no_access_in, no_access_out, inap, pic_plat_masuk, pic_plat_keluar) VALUES ('000000', 'TEST', 'A', 0, NULL, 'PK1', '2014-05-21 14:00:00', '2014-05-21 14:40:49', NULL, '00001', NULL, 'S2', NULL, '0', NULL, 2000, NULL, '2014-05-21 14:40:49', NULL, '', NULL, '', NULL, NULL, 0, NULL, NULL, NULL, '2014-05-21 13:45:00', 0, 0, NULL, NULL, NULL, NULL, 0, NULL, NULL, NULL, 0, '', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, '', '', NULL, NULL, NULL, NULL, NULL);


--
-- TOC entry 2366 (class 0 OID 16829)
-- Dependencies: 225
-- Data for Name: transaksi_parkir_driver; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2367 (class 0 OID 16835)
-- Dependencies: 226
-- Data for Name: transaksi_parkir_gambar; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2368 (class 0 OID 16841)
-- Dependencies: 227
-- Data for Name: transaksi_parkir_inap; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2369 (class 0 OID 16848)
-- Dependencies: 228
-- Data for Name: transaksi_pulsa; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2335 (class 0 OID 16618)
-- Dependencies: 185
-- Data for Name: transaksi_stiker; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2370 (class 0 OID 16855)
-- Dependencies: 229
-- Data for Name: transaksi_stiker_res; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO transaksi_stiker_res (notrans, nama, alamat, telepon, jenis_transaksi, awal, harga, keterangan, tanggal, operator, akhir, maks, no_id, unit_kerja, no_induk, nopol, jenis_mobil, adm) VALUES ('0023/STK/03/2018', 'A.azis', '', '', 0, '2018-03-05 00:00:00', 0, 'PERUBAHAN DATA', '2018-03-25 19:13:24', '00001', '2018-08-31 23:59:59', 1, '0023/IDT/03/2018', '10', '', 'DD2186AY', 'C', '00001');


--
-- TOC entry 2371 (class 0 OID 16862)
-- Dependencies: 230
-- Data for Name: valet; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2372 (class 0 OID 16869)
-- Dependencies: 231
-- Data for Name: valet_cust_info; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2373 (class 0 OID 16872)
-- Dependencies: 232
-- Data for Name: valet_out; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO valet_out (notrans, valet_nopol, barcode, waktu_keluar, waktu_masuk, valet_charge, valet_adm, waktu_valet, valet_ops, login_waktu_valet, jenis_valet_out) VALUES ('020014', 'B634LP', NULL, '2009-05-23 15:22:53', '2009-05-14 09:23:33', 15000, '00001', '2009-05-23 14:31:33.601539', '22', '2009-05-23 06:50:00', NULL);
INSERT INTO valet_out (notrans, valet_nopol, barcode, waktu_keluar, waktu_masuk, valet_charge, valet_adm, waktu_valet, valet_ops, login_waktu_valet, jenis_valet_out) VALUES ('020015', 'B1LP', NULL, '2009-05-23 15:23:53', '2009-05-14 09:23:00', 15000, '00001', '2009-05-23 15:23:19.045182', '22', '2009-05-23 14:50:00', NULL);
INSERT INTO valet_out (notrans, valet_nopol, barcode, waktu_keluar, waktu_masuk, valet_charge, valet_adm, waktu_valet, valet_ops, login_waktu_valet, jenis_valet_out) VALUES (NULL, '1', NULL, NULL, NULL, NULL, '00001', '2009-06-09 12:10:37.958083', '1', '2009-06-09 06:50:00', NULL);
INSERT INTO valet_out (notrans, valet_nopol, barcode, waktu_keluar, waktu_masuk, valet_charge, valet_adm, waktu_valet, valet_ops, login_waktu_valet, jenis_valet_out) VALUES ('90002', 'B1111AA', NULL, '2009-07-09 15:33:54', '2009-07-09 12:39:12', 0, '00001', '2009-07-09 11:55:22.973085', '', '2009-07-09 06:00:00', NULL);


--
-- TOC entry 2374 (class 0 OID 16875)
-- Dependencies: 233
-- Data for Name: video_counter; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2375 (class 0 OID 16881)
-- Dependencies: 234
-- Data for Name: vod; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 2290 (class 2606 OID 17459)
-- Dependencies: 231 231
-- Name: valet_cust_info_pk; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY valet_cust_info
    ADD CONSTRAINT valet_cust_info_pk PRIMARY KEY (nopol);


--
-- TOC entry 2265 (class 1259 OID 17460)
-- Dependencies: 192 192 192 192 192
-- Name: Full_Transaksi_Parkir; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX "Full_Transaksi_Parkir" ON transaksi_parkir USING btree (id, id_kendaraan, no_pol, status, veri_check);


--
-- TOC entry 2275 (class 1259 OID 17461)
-- Dependencies: 194 194 194 194 194
-- Name: Full_parkir_transaksi; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX "Full_parkir_transaksi" ON parkir_transaksi USING btree (id, id_kendaraan, no_pol, status, veri_check);


--
-- TOC entry 2266 (class 1259 OID 17462)
-- Dependencies: 192 192 192 192
-- Name: Transaksi_park_idx1; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX "Transaksi_park_idx1" ON transaksi_parkir USING btree (status_transaksi, id_kendaraan, waktu_keluar, pklogin);


--
-- TOC entry 2262 (class 1259 OID 17463)
-- Dependencies: 159 159
-- Name: det_stiker_idx; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX det_stiker_idx ON detail_transaksi_stiker USING btree (nopol, notrans);


--
-- TOC entry 2261 (class 1259 OID 17464)
-- Dependencies: 154 154 154 154
-- Name: detail_langganan_full_index; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX detail_langganan_full_index ON detail_langganan USING btree (id_langganan, nopol, jenis, akses);


--
-- TOC entry 2267 (class 1259 OID 17465)
-- Dependencies: 192 192 192
-- Name: id_kendaraan_idx; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX id_kendaraan_idx ON transaksi_parkir USING btree (id_kendaraan, no_pol, veri_check);


--
-- TOC entry 2276 (class 1259 OID 17466)
-- Dependencies: 194 194 194
-- Name: id_kendaraan_parkir_idx; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX id_kendaraan_parkir_idx ON parkir_transaksi USING btree (id_kendaraan, no_pol, veri_check);


--
-- TOC entry 2287 (class 1259 OID 17467)
-- Dependencies: 226 226 226
-- Name: join_gambar_idx; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX join_gambar_idx ON transaksi_parkir_gambar USING btree (notrans, waktu, id_pos);


--
-- TOC entry 2263 (class 1259 OID 17468)
-- Dependencies: 173 173 173 173 173 173
-- Name: langganan_full_index; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX langganan_full_index ON langganan USING btree (id, enable, keyid, jenis_langganan, awal, akhir);


--
-- TOC entry 2268 (class 1259 OID 17469)
-- Dependencies: 192 192
-- Name: nopol_idx; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX nopol_idx ON transaksi_parkir USING btree (no_pol, status);


--
-- TOC entry 2277 (class 1259 OID 17470)
-- Dependencies: 194 194
-- Name: nopol_transaksi_idx; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX nopol_transaksi_idx ON parkir_transaksi USING btree (no_pol, status);


--
-- TOC entry 2278 (class 1259 OID 17471)
-- Dependencies: 194 194 194 194
-- Name: park_transaksi_idx1; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX park_transaksi_idx1 ON parkir_transaksi USING btree (status_transaksi, id_kendaraan, waktu_keluar, pklogin);


--
-- TOC entry 2279 (class 1259 OID 17472)
-- Dependencies: 194 194
-- Name: parkir_transaksi_idx; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX parkir_transaksi_idx ON parkir_transaksi USING btree (status, veri_check);


--
-- TOC entry 2280 (class 1259 OID 17473)
-- Dependencies: 194 194 194
-- Name: parkir_transaksi_keluar.idx; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX "parkir_transaksi_keluar.idx" ON parkir_transaksi USING btree (status, pklogin, id_op_keluar);


--
-- TOC entry 2281 (class 1259 OID 17474)
-- Dependencies: 194 194
-- Name: parkir_transaksi_waktu_masuk.idx; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX "parkir_transaksi_waktu_masuk.idx" ON parkir_transaksi USING btree (no_pol, waktu_masuk);


--
-- TOC entry 2269 (class 1259 OID 17475)
-- Dependencies: 192 192
-- Name: pintu_masuk_idx; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX pintu_masuk_idx ON transaksi_parkir USING btree (id_pintu_masuk, waktu_masuk);


--
-- TOC entry 2282 (class 1259 OID 17476)
-- Dependencies: 194 194
-- Name: pintu_masuk_transaksi_idx; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX pintu_masuk_transaksi_idx ON parkir_transaksi USING btree (id_pintu_masuk, waktu_masuk);


--
-- TOC entry 2270 (class 1259 OID 17477)
-- Dependencies: 192 192 192
-- Name: status_parkir_idx; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX status_parkir_idx ON transaksi_parkir USING btree (status, id_pintu_keluar, waktu_keluar);


--
-- TOC entry 2283 (class 1259 OID 17478)
-- Dependencies: 194 194 194
-- Name: status_parkir_transaksi_idx; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX status_parkir_transaksi_idx ON parkir_transaksi USING btree (status, id_pintu_keluar, waktu_keluar);


--
-- TOC entry 2285 (class 1259 OID 17479)
-- Dependencies: 211
-- Name: stok_barcode_kode_idx; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX stok_barcode_kode_idx ON stok_barcode USING btree (code);


--
-- TOC entry 2286 (class 1259 OID 17481)
-- Dependencies: 211
-- Name: stok_barcode_status_idx; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX stok_barcode_status_idx ON stok_barcode USING btree (status);


--
-- TOC entry 2264 (class 1259 OID 17482)
-- Dependencies: 185 185
-- Name: trans_stiker_idx; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX trans_stiker_idx ON transaksi_stiker USING btree (notrans, tgl_edited);


--
-- TOC entry 2271 (class 1259 OID 17483)
-- Dependencies: 192 192 192
-- Name: transaksi_keluar.idx; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX "transaksi_keluar.idx" ON transaksi_parkir USING btree (status, pklogin, id_op_keluar);


--
-- TOC entry 2272 (class 1259 OID 17484)
-- Dependencies: 192 192
-- Name: transaksi_parkir_idx; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX transaksi_parkir_idx ON transaksi_parkir USING btree (status, veri_check);


--
-- TOC entry 2273 (class 1259 OID 17485)
-- Dependencies: 192 192
-- Name: valet_idx; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX valet_idx ON transaksi_parkir USING btree (valet_adm, login_waktu_valet);


--
-- TOC entry 2284 (class 1259 OID 17486)
-- Dependencies: 194 194
-- Name: valet_parkir_transaksi_idx; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX valet_parkir_transaksi_idx ON parkir_transaksi USING btree (valet_adm, login_waktu_valet);


--
-- TOC entry 2288 (class 1259 OID 17487)
-- Dependencies: 226 226 226
-- Name: waktu_gambar_idx; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX waktu_gambar_idx ON transaksi_parkir_gambar USING btree (waktu, id_pos, notrans);


--
-- TOC entry 2274 (class 1259 OID 17488)
-- Dependencies: 192 192
-- Name: waktu_masuk.idx; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX "waktu_masuk.idx" ON transaksi_parkir USING btree (no_pol, waktu_masuk);


--
-- TOC entry 2291 (class 2620 OID 17489)
-- Dependencies: 236 192
-- Name: on_transaksi_parkir_audit; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER on_transaksi_parkir_audit
    AFTER INSERT OR DELETE OR UPDATE ON transaksi_parkir
    FOR EACH ROW
    EXECUTE PROCEDURE on_audit();


--
-- TOC entry 2292 (class 2620 OID 17490)
-- Dependencies: 192 248
-- Name: transaksi_parkir_cannot_delete; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER transaksi_parkir_cannot_delete
    AFTER DELETE ON transaksi_parkir
    FOR EACH ROW
    EXECUTE PROCEDURE transaksi_parkir_cannot_delete();


--
-- TOC entry 2380 (class 0 OID 0)
-- Dependencies: 6
-- Name: public; Type: ACL; Schema: -; Owner: -
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


-- Completed on 2018-05-26 10:09:37

--
-- PostgreSQL database dump complete
--

