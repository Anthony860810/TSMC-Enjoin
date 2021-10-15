import { createApp } from "https://cdnjs.cloudflare.com/ajax/libs/vue/3.0.9/vue.esm-browser.prod.js";

createApp({
  data() {
    return {
      apiUrl: ``,
      //apiUrl: `http://127.0.0.1:5000`,
      user: {
        id: "",
        password: "",
      },
      register: {
        id: "",
        password: "",
        epidemic_prevention_group: ""
      },
    };
  },
  methods: {
    create() {
      let button = document.getElementById("registerBTN");
      button.disabled = true;
      axios
        .post(`${this.apiUrl}/Account/Create`, this.register)
        .then((res) => {
          console.log(res);
          alert(res.data.message);
          button.disabled = false;
          window.location.href = `/`;
        })
        .catch((err) => {
          console.log(err);
        });
    },
  },
}).mount("#app");
