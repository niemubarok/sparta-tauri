import { useTransaksiStore } from "src/stores/transaksi-store";
import ls from "localstorage-slim";
const transaksiStore = useTransaksiStore();
export const zeroPad = (n) => {
  return (n < 10 ? "0" : "") + n;
};

export const dayName = [
  "Minggu",
  "Senin",
  "Selasa",
  "Rabu",
  "Kamis",
  "Jum'at",
  "Sabtu",
];

export const getDayName = (date) => {
  const initDate = new Date(date);
  const day = initDate.getDay();

  return day == 0 ? dayName[0] : dayName[day];
};

export const getTime = () => {
  const currentDate = new Date();
  const today = currentDate.getDay();
  const date = currentDate.getDate();
  const month = currentDate.getMonth();
  const year = currentDate.getFullYear();
  const day = getDayName(currentDate);
  const hours = zeroPad(currentDate.getHours());
  const minutes = zeroPad(currentDate.getMinutes());
  const seconds = zeroPad(currentDate.getSeconds());
  return {
    year,
    today,
    day,
    date,
    hours,
    minutes,
    seconds,
    fullDate: date + "/" + (month + 1) + "/" + year,
    time: hours + ":" + minutes + ":" + seconds,
  };
};

export const formatDate = (dateString) => {
  const date = new Date(dateString);
  const day = date.getDate().toString().padStart(2, '0');
  const month = (date.getMonth() + 1).toString().padStart(2, '0');
  const year = date.getFullYear();
  return `${day}/${month}/${year}`;
};

export const formatTime = (dateString) => {
  const date = new Date(dateString);
  const hours = date.getHours().toString().padStart(2, '0');
  const minutes = date.getMinutes().toString().padStart(2, '0');
  const seconds = date.getSeconds().toString().padStart(2, '0');
  return `${hours}:${minutes}:${seconds}`;
};

export const calculateParkingTime = (entryTime, exitTime) => {
  const entry = new Date(entryTime);
  const exit = exitTime ? new Date(exitTime) : new Date();
  const diffInMilliseconds = exit - entry;

  const hours = Math.floor(diffInMilliseconds / (1000 * 60 * 60));
  const minutes = Math.floor((diffInMilliseconds % (1000 * 60 * 60)) / (1000 * 60));
  
  return {
    hours,
    minutes,
    totalMinutes: hours * 60 + minutes,
    totalHours: Math.ceil(hours + minutes/60)
  };
};

export const setTime = (h, m, s) => {
  const currentDate = new Date();
  currentDate.setHours(h, m, s);

  return {
    hours: zeroPad(currentDate.getHours()),
    minutes: zeroPad(currentDate.getMinutes()),
  };
};

export const compareTime = (time1, time2, comparison) => {
  const [hour1, minute1, second1] = time1.split(":");
  const [hour2, minute2, second2] = time2.split(":");

  const date1 = new Date(2022, 0, 1, +hour1, +minute1, +second1).getTime();
  const date2 = new Date(2022, 0, 1, +hour2, +minute2, +second2).getTime();

  if (comparison == "equal") {
    return date1 == date2;
  } else if (comparison == "lt") {
    return date1 < date2;
  } else if (comparison == "gt") {
    return date1 > date2;
  }
};

export const timeToMillisecond = (t) => {
  if (t) {
    return (
      Number(t.split(":")[0]) * 3600000 +
      Number(t.split(":")[1]) * 60000 +
      Number(t.split(":")[2]) * 1000
    );
  }
};

export const addMinutes = (t, m) => {
  const time = new Date(
    new Date("1970/01/01 " + t).getTime() + m * 60000
  ).toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });

  return time;
};

export const isValidTime = (time) => {
  return /^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$/gm.test(time);
};

export const checkSubscriptionExpiration = (subscriptionEndDate) => {
  const currentDate = new Date().setHours(0, 0, 0, 0);
  const endDate = new Date(subscriptionEndDate).setHours(0, 0, 0, 0);

  if (currentDate < endDate) {
    const timeDiff = endDate - currentDate;
    const daysLeft = Math.floor(timeDiff / (1000 * 3600 * 24));
    // const hoursLeft = Math.floor((timeDiff % (1000 * 3600 * 24)) / (1000 * 3600));
    // const minutesLeft = Math.floor((timeDiff % (1000 * 3600)) / (1000 * 60));
    transaksiStore.isMemberExpired = false;
    // return `Berakhir pada ${daysLeft} hari, ${hoursLeft} jam, ${minutesLeft} menit, dan ${secondsLeft} detik.`;
    return `Berakhir dalam ${daysLeft} hari (${new Date(
      subscriptionEndDate
    ).toLocaleDateString("id-ID")})`;
    return;
  } else {
    transaksiStore.isMemberExpired = true;
    return `Langganan sudah berakhir pada ${new Date(
      subscriptionEndDate
    ).toLocaleDateString("id-ID")}`;
  }
};

export const calculateParkingDuration = (entryTime) => {
  const currentTime = new Date();
  const targetTime = new Date(entryTime);
  const diffInMilliseconds = currentTime - targetTime;

  const days = Math.floor(diffInMilliseconds / (1000 * 60 * 60 * 24));
  const hours = Math.floor(diffInMilliseconds / (1000 * 60 * 60));
  const minutes = Math.floor(
    (diffInMilliseconds % (1000 * 60 * 60)) / (1000 * 60)
  );
  const seconds = Math.floor((diffInMilliseconds % (1000 * 60)) / 1000);

  const interval24 = Math.floor(hours / 24); // Use Math.floor instead of Math.round to get the correct number of 24-hour intervals
  const additionalHourAfter24 = hours - interval24 * 24;

  return { days, hours, minutes, seconds, additionalHourAfter24 };
};

// export const determineShift = () => {
//   const shift1Start = "07:00";
//   const shift1End = "14:00";
//   const shift2Start = "14:01";
//   const shift2End = "21:00";

//   const is24HourFormat = !new Date().toLocaleTimeString().match(/am|pm/i);

//   let currentTime = new Date().toLocaleTimeString([], {
//     hour12: is24HourFormat,
//     hour: "2-digit",
//     minute: "2-digit",
//   });
//   // console.log(!is24HourFormat);

//   if (is24HourFormat) {
//     const timeParts = currentTime.match(/(\d+):(\d+)(am|pm)/i);
//     if (timeParts) {
//       let [_, hour, minute, meridiem] = timeParts;
//       hour = parseInt(hour, 10);
//       if (meridiem.toLowerCase() === "pm" && hour < 12) {
//         hour += 12;
//       } else if (meridiem.toLowerCase() === "am" && hour === 12) {
//         hour = 0;
//       }
//       currentTime = `${hour.toString().padStart(2, "0")}:${minute}`;
//       console.log(currentTime);
//     }
//   } else {
//     currentTime = currentTime.replace(/[^0-9:]/g, ""); // Remove AM/PM if present
//   }

//   if (currentTime >= shift1Start && currentTime <= shift1End) {
//     shift.value = "S1";
//   } else if (currentTime >= shift2Start && currentTime <= shift2End) {
//     shift.value = "S2";
//   } else {
//     shift.value = "S3";
//   }

//   ls.set("shift", shift.value);
// };
export const timeRegex24Format =
  /^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$/gm;
