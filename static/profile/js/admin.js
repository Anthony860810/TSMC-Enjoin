import { createApp } from "https://cdnjs.cloudflare.com/ajax/libs/vue/3.0.9/vue.esm-browser.prod.js";
const apiUrl = "";
//const apiUrl = `http://127.0.0.1:5000`;

let orderModal = null;
let closeOrderModal = null;
let delOrderModal = null;
let followModal = null;
//let token = null;
const token = document.cookie.replace(
  /(?:(?:^|.*;\s*)Token\s*=\s*([^;]*).*$)|^.*$/,
  "$1"
);
const COOKIE_id = document.cookie.replace(
  /(?:(?:^|.*;\s*)_id\s*=\s*([^;]*).*$)|^.*$/,
  "$1"
);
const COOKIEid = document.cookie.replace(
  /(?:(?:^|.*;\s*)id\s*=\s*([^;]*).*$)|^.*$/,
  "$1"
);

//console.log(token);
//console.log(COOKIE_id);
//console.log(COOKIEid);
//const url = new URL(window.location.href);
//const param = url.searchParams.get("id");
const param = COOKIEid;

function removeCookie(name) {
    document.cookie = name + '=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
}

createApp({
  data() {
    return {
      followList : [],
      ownList : [],
      isNew: false,
      tempOrder: {
      },
    };
  },
  mounted() {
    orderModal = new bootstrap.Modal(
      document.getElementById("orderModal"),
      {
        keyboard: false,
      }
    );
    closeOrderModal = new bootstrap.Modal(
      document.getElementById("closeOrderModal"),
      {
        keyboard: false,
      }
    );
    followModal = new bootstrap.Modal(
      document.getElementById("followModal"),
      {
        keyboard: false,
      }
    );
    delOrderModal = new bootstrap.Modal(
      document.getElementById("delOrderModal"),
      {
        keyboard: false,
      }
    );
    
   /*
    token = document.cookie.replace(
      /(?:(?:^|.*;\s*)Token\s*=\s*([^;]*).*$)|^.*$/,
      "$1"
    );
    */

    /*
    if (token === "") {
      alert("請重新登入");
      window.location = "../LoginRegister";
    }
    axios.defaults.headers.common.Authorization = token;
    */
   
    /*
    const url = new URL(window.location.href);
    param = url.searchParams.get("id");
    */
    this.getOwnerGroupOrder();
  },
  methods: {
    getOwnerGroupOrder(){
      //getData(page = 1) {
        console.log(token)
        axios
          .get(`${apiUrl}/Account/ListOwnerCreatedGroupOrder/${param}`,{
            headers: {
            'x-access-token': token
            }
          })
          //.get(`${apiUrl}/${apiPath}/admin/products?page=${page}`)
          .then((res) => {
            //console.log(res);
            //console.log(res.data);
            if (res.data.message==='success') {
              this.ownList = res.data.data;
            } else {
              alert(res.data.message);
            }
          })
          .catch((err) => {
            console.log(err);
          });
    },
    getAllGroupOrder(){
    //getData(page = 1) {
      console.log(token)
      axios
        .get(`${apiUrl}/Account/ListOwnerGroupOrder/${param}`,{
          headers: {
          'x-access-token': token
          }
        })
        //.get(`${apiUrl}/${apiPath}/admin/products?page=${page}`)
        .then((res) => {
          //console.log(res);
          //console.log(res.data);
          if (res.data.message==='success') {
            this.followList = res.data.data;
            followModal.show();
          } else {
            alert(res.data.message);
          }
        })
        .catch((err) => {
          console.log(err);
        });
    },

    updateOrder() {
      let checkValidate = false;
      let timeDiff_positive = false;
      if(this.tempOrder.title && this.tempOrder.store && this.tempOrder.drink 
        && this.tempOrder.meet_factory && this.tempOrder.join_people_bound 
        && this.tempOrder.meet_factory && this.tempOrder.meet_time_start && this.tempOrder.meet_time_end)
        { 
          checkValidate = true;
          if(new Date(this.tempOrder.meet_time_end) - new Date(this.tempOrder.meet_time_start)>0)
          {
            timeDiff_positive = true;
          }
        }
      if(checkValidate && timeDiff_positive)
      {
        let url = ``;
        let http = "";
        let button = document.getElementById("orderModal_confirmBTN");
        if (!this.isNew) {
          button.disabled = true;
          url = `${apiUrl}/Account/UpdateOrder/${param}/${this.tempOrder._id}`;
          http = "post";

          axios[http](url,
            this.tempOrder,
            {headers: {'x-access-token': token}},
          )
          .then((res) => {
            button.disabled=false;
            if (res.data.message==="編輯揪團單子成功") {
              alert(res.data.message);
              orderModal.hide();
              this.getOwnerGroupOrder();
            } else {
              alert(res.data.message);
            }
          })
          .catch((err) => {
            console.log(err);
          });
        }
        else
        {
          url = `${apiUrl}/Account/CreateOrder/${param}`;
          http = "post";
          button.disabled = true;

          axios[http](url,
            this.tempOrder,
            {headers: {'x-access-token': token}},
          )
          .then((res) => {
            button.disabled = false;
            if (res.data.message==="建立揪團單子成功") {
              alert(res.data.message);
              orderModal.hide();
              this.getOwnerGroupOrder();
            } else {
              alert(res.data.message);
            }
          })
          .catch((err) => {
            console.log(err);
          });
        }

        /*
        const formData = new FormData();
        formData.append('meet_factory', this.tempOrder.meet_factory);
        formData.append('store', this.tempOrder.store);
        formData.append('drink', this.tempOrder.drink);
        formData.append('meet_time_start', this.tempOrder.meet_time_start);
        formData.append('meet_time_end',this.tempOrder.meet_time_end);
        formData.append('comment', this.tempOrder.comment);
        formData.append('title', this.tempOrder.title);
        //formData.append('hashtag', this.tempOrder.hashtag);
        formData.append('join_people_bound', this.tempOrder.join_people_bound);
        */
      }
      else if(checkValidate && !timeDiff_positive)
      {
        alert("結束時間與開始時間有誤!(結束時間應大於開始時間)");
      }
      else
      {
        alert("請確認必填欄位是否都已填寫!");
      }
      
    },

    closeOrder(){
      let button = document.getElementById("closeOrderModal_confirmBTN");
      button.disabled = true;
      axios
        .post(`${apiUrl}/Account/CloseOrder/${param}/${this.tempOrder._id}`,{},{
          headers: {'x-access-token': token}
        })
        .then((res) => {
          button.disabled = false;
          if (res.data.message==="更新status成功") {
            alert("更新揪團狀態成功!揪團已成立!");
            closeOrderModal.hide();
            this.getOwnerGroupOrder();
          } else {
            alert(res.data.message);
          }
        })
        .catch((err) => {
          console.log(err);
        });
    },

    delOrder() {
      let button = document.getElementById("delOrderModal_confirmBTN");
      button.disabled = true;
      axios
        .delete(`${apiUrl}/Account/DeleteCreatedOrder/${param}/${this.tempOrder._id}`,{
          headers: {'x-access-token': token}
        })
        .then((res) => {
          button.disabled = false;
          if (res.data.message==="刪除單子成功") {
            alert(res.data.message);
            delOrderModal.hide();
            this.getOwnerGroupOrder();
          } else {
            console.log(res.data.message);
          }
        })
        .catch((err) => {
          console.log(err);
        });
    },

    leaveOrder(item){
      this.tempOrder = {...item};
      axios
        .post(`${apiUrl}/Order/QuitOrder/${COOKIE_id}/${this.tempOrder._id}`,{
          headers: {'x-access-token': token}
        })
        .then((res) => {
          if (res.data.message==="Remove Success!") {
            alert("退出揪團成功!");
            this.getAllGroupOrder();
          } else {
            console.log(res.data.message);
            alert(res.data.message);
          }
        })
        .catch((err) => {
          console.log(err);
        });
    },


    openModal(status, item) {
      if(status === "newOrder")
      {
        this.tempOrder = {
          id: param,
        };
        this.isNew = true;
        orderModal.show();
      }
      else if(status === "editOrder")
      {
        if (!('comment' in item)) {
          item.comment = ''
        }
        this.tempOrder = {
          ...item,
          meet_time_start: item.meet_time[0],
          meet_time_end: item.meet_time[1]
        };
        delete this.tempOrder.meet_time; 
        this.isNew = false;
        orderModal.show();
      }
      else if(status === "closeOrder")
      {
        this.tempOrder = {...item};
        closeOrderModal.show();
      }
      else if (status === "deleteOrder") {
        this.tempOrder = { ...item };
        delOrderModal.show();
      }
    },

    checkStatus(value){
      if(value==='IN_PROGRESS'){
        return '揪團中';
      }
      else if(value==='COMPLETED')
      {
        return '已滿';
      }
      else if(value==='CLOSED')
      {
        return '已成立';
      }
      return value;
    },

    formatDate(value,type) {
        let tmp = value;
        tmp = String(tmp).replace('T',' ');
        tmp = String(tmp).replace('Z',' ');
        if(type===0)
        {
          return "自: "+tmp;
        }
        else if(type===1)
        {
          return "至: "+tmp;
        }
        return tmp;
    },
    
    logout() {
      removeCookie('Token');
      removeCookie('_id');
      removeCookie('id');
      window.location.replace('/')
      // alert("登出成功!!");
      // window.location = "../LoginRegister";
    },
  },
}).mount("#app");
