"use strict";

async function getStatistics() {
  try {
    const response = await fetch("acc_info");
    const data = await response.json();
    const responseGoldenBride = await fetch(
      "https://goldenbride.net/usermodule/services/agencyhelper?command=finances",
      {
        method: "POST",
        body: new URLSearchParams({
          login: `${data.login}`,
          pass: `${data.password}`,
          ladyID: `${data.login}`,
          from: "2024-10-19",
          to: "2024-10-20",
        }),
      }
    );
    const allOperations = await responseGoldenBride.json();

    const { total } = allOperations;
    const { list } = allOperations;
    list.forEach((element) => {
      console.log(
        `🆔 ${element.ladyID}/ 💲 ${element.sum}/ 💌 '${element.operation}'`
      );
    });
  } catch (err) {
    console.log(err);
  }
}

getStatistics();
