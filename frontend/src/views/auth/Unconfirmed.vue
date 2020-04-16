<template>
  <div class="container">
    <alert
      v-for="(alert, index) in alerts"
      :key="index"
      v-bind:variant="alert.variant"
      v-bind:message="alert.message"
    ></alert>

    <h5 class="h5 g-color-gray-dark-v1 mb-0">
      <span class="g-color-red">Need another confirmation email?</span>
      <button v-on:click="onResendConfirm()" type="button" class="btn btn-primary">Click here</button>
    </h5>
  </div>
</template>

<script>
import store from "@/store";
import Alert from "./Alert";
import { getUser, getConfirm, resendConfirm } from "@/api/user";

export default {
  name: "Confirm",
  components: {
    alert: Alert
  },
  data() {
    return {
      user: "",
    };
  },
  methods: {
    getUserInfo(id) {
      getUser(id).then(response => {
          // handle success
          this.user = response.data;
          this.$message({
            message: `Hello, ${this.user.name || this.user.username} Welcome!!`,
            type: 'success'
          })
        })
        .catch(error => {
          // handle error
          console.error(error);
        });
    },
    onResendConfirm() {
      const payload = {
        confirm_email_base_url:
          window.location.href.split("/", 4).join("/") + "/unconfirmed/?token="
      };
      resendConfirm(payload).then(response => {
          // handle success
          this.$message({
            message: response.msg,
            type: 'success'
          });
        })
        .catch(error => {
          // handle error
          console.log(error.response.data);
          this.$toasted.error(error.response.data.message, {
            icon: "fingerprint"
          });
        });
    },
    onConfirm(token) {
        getConfirm(token).then(response => {
          console.log(response)
          // handle success
          this.$message({
            message: response.msg,
            type: 'success'
          });
          // 更新 JWT
          // window.localStorage.setItem("token", response.token);
          // store.loginAction();
          // 路由跳转
         this.$router.push("/");
        })
        .catch(error => {
          // handle error
          this.$toasted.error(error.response.msg, {
            icon: "fingerprint"
          });
        });
    }
  },
  created() {
    // 点击邮件中的链接后，确认账户
    if (store.getters.token) {
      this.onConfirm(store.getters.token);
    }

    // 未确认的用户，显示提示信息
    const user_id = store.getters.userid;
    this.getUserInfo(user_id);
  }
};
</script>
