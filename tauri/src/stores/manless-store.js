import { defineStore } from "pinia";
import { calculateParkingDuration } from "src/utils/time-util";

export const useManlessStore = defineStore("manless", {
  state: () => ({
    biayaParkir: 0,
    isMember: false,
    isMemberExpired: false
  }),

  getters: {
    isMemberActive(state) {
      return state.isMember && !state.isMemberExpired;
    },
  },

  actions: {
   async getTransactionByPlateNumber(plateNumber) {
      try {
        const result = await localDb.find({
          selector: {
            type: 'transaction',
            plate_number: plateNumber,
            status: 1 // Assuming 1 is active transaction
          }
        });

        if (result.docs.length === 0) {
          return null;
        }

        return result.docs[0];
      } catch (error) {
        console.error("Error fetching transaction:", error);
        throw error;
      }
    },
     async saveTransaction(transaction) {
      try {
        const doc = {
          _id: new Date().toISOString(), // or use a specific ID format
          type: 'transaction',
          ...transaction,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        };

        const response = await localDb.put(doc);
        return response;
      } catch (error) {
        console.error("Error saving transaction:", error);
        throw error;
      }
    },
    parkingDuration(entryTime) {
      const duration = calculateParkingDuration(entryTime);
      return duration.days > 0
        ? duration.additionalHourAfter24 !== 0
          ? `${duration.days} Hari ${duration.additionalHourAfter24} Jam ${duration.minutes} Menit`
          : `${duration.days} Hari ${duration.minutes} Menit`
        : duration.hours > 0
        ? `${duration.hours} Jam ${duration.minutes} Menit`
        : `${duration.minutes} Menit`;
    },
    async calculateParkingFee(entryTime, waktuKeluar) {
      if (this.isMember && !this.isMemberExpired) {
        return 0;
      } else {
        const tarif = await this.getTarifJenisKendaraan();
        const tarifAwal = parseInt(tarif?.tarif);
        const tarifBerikutnya = parseInt(tarif?.tarif_interval);
        const tarifMaksimal = parseInt(tarif?.maksimum);
        const interval = parseInt(tarif?.interval);

        const currentTime = new Date();
        const targetTime = new Date(entryTime);
        const diffInMilliseconds = currentTime - targetTime;

        const durationInHour = Math.floor(
          diffInMilliseconds / (1000 * 60 * 60)
        );

        const interval24 = Math.floor(durationInHour / 24);
        // console.log("durationInHour", durationInHour);

        // Calculate the additional fee
        let additionalFee = durationInHour * tarifBerikutnya;
        let totalFee = 0;

        //jika dibawah 1 jam pakai tarif awal
        if (durationInHour <= 1) {
          totalFee = tarifAwal;
        }
        //jika diatas 1 jam tarif awal + tarif berikutnya
        else if (durationInHour > 1) {
          totalFee += additionalFee;
        }
        //jika total tarif lebih dari tarif maksimal
        if (totalFee > tarifMaksimal) {
          totalFee = tarifMaksimal;
        }

        // Calculate the number of 24-hour intervals
        const additionalHourAfter24 = durationInHour - interval24 * 24;
        // console.log("additionalHourAfter24", additionalHourAfter24);
        let additionalFeeAfter24 = additionalHourAfter24 * tarifBerikutnya;
        //jika lebih dari 24 jam tarif maksimal + tarif berikutnya
        if (interval24 > 0) {
          if (additionalFeeAfter24 > tarifMaksimal) {
            additionalFeeAfter24 = tarifMaksimal;
          }
          // console.log("additionalFeeAfter24", additionalFeeAfter24);
          totalFee = interval24 * tarifMaksimal + additionalFeeAfter24;
        }
        // console.log("interval24", interval24);
        if (this.isMember && !this.isMemberExpired) {
          totalFee = 0;
        }
        totalFee = Math.round(totalFee);

        this.biayaParkir = totalFee;
        return totalFee;
      }
    },
    // In your Vue component where you construct the camera URL
    async getCameraFeed() {
      const encodedUrl = encodeURIComponent(
        "http://admin:Hiks2024@192.168.10.25/ISAPI/streaming/channels/1/picture"
      );
      const proxyUrl = `${
        process.env.API_URL || "http://localhost:3333"
      }/api/cctv/camera-feed?url=${encodedUrl}`;

      try {
        const response = await fetch(proxyUrl, {
          credentials: "include",
          headers: {
            Accept: "image/jpeg",
          },
        });
        if (!response.ok) throw new Error("Network response was not ok");
        return await response.blob();
      } catch (error) {
        console.error("Error fetching camera feed:", error);
        throw error;
      }
    },
  },
});
