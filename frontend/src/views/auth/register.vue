<template>
  <div class="login-container">
    <el-form
      ref="registerForm"
      :model="registerForm"
      :rules="loginRules"
      class="login-form"
      auto-complete="on"
      label-position="left"
    >
      <div class="title-container">
        <h3 class="title">注册新用户</h3>
      </div>

      <el-form-item prop="username">
        <span class="svg-container">
          <svg-icon icon-class="user" />
        </span>
        <el-input
          ref="username"
          v-model="registerForm.username"
          placeholder="账户名"
          name="username"
          type="text"
          tabindex="1"
        />
      </el-form-item>

      
      <el-form-item prop="contact">
        <span class="svg-container">
          <svg-icon icon-class="user" />
        </span>
        <el-input
          ref="contact"
          v-model="registerForm.contact"
          placeholder="联系人"
          name="contact"
          type="text"
          tabindex="1"
        />
      </el-form-item>

      <el-form-item prop="email">
        <span class="svg-container">
          <svg-icon icon-class="user" />
        </span>
        <el-input
          ref="email"
          v-model="registerForm.email"
          placeholder="电子邮箱"
          name="email"
          type="text"
          tabindex="1"
          auto-complete="on"
        />
      </el-form-item>

      <el-form-item prop="password">
        <span class="svg-container">
          <svg-icon icon-class="password" />
        </span>
        <el-input
          :key="passwordType"
          ref="password"
          v-model="registerForm.password"
          :type="passwordType"
          placeholder="密码"
          name="password"
          tabindex="2"
          @keyup.enter.native="handleLogin"
        />
        <span class="show-pwd" @click="showPwd">
          <svg-icon :icon-class="passwordType === 'password' ? 'eye' : 'eye-open'" />
        </span>
      </el-form-item>

      <el-form-item>
        <span class="svg-container">
          <svg-icon icon-class="password" />
        </span>
        <el-input
          :key="passwordType"
          ref="confirmed"
          v-model="registerForm.confirmed"
          :type="passwordType"
          placeholder="确认密码"
          name="confirmed"
          tabindex="2"
          @keyup.enter.native="handleLogin"
        />
        <span class="show-pwd" @click="showPwd">
          <svg-icon :icon-class="passwordType === 'password' ? 'eye' : 'eye-open'" />
        </span>
      </el-form-item>
      <el-button
        type="primary"
        style="width:100%;margin-bottom:30px;"
        @click.native.prevent="handleLogin"
      >注册</el-button>

      <el-button><router-link to='/login'>返回登录页面</router-link></el-button>
    </el-form>
  </div>
</template>

<script>
import { validUsername } from "@/utils/validate";
import { postUsers } from "@/api/user";
export default {
  name: "Register", //this is the name of the component
  data() {
    const validateUsername = (rule, value, callback) => {
      callback();
    };
    const validatePassword = (rule, value, callback) => {
      if (value.length < 6) {
        callback(new Error("密码不得小于6个数字"));
      } else if (value !== this.registerForm.confirmed) {
        callback(new Error("密码与确认密码必须一致"));
      } else {
        callback();
      }
    };
    const validateEmail = (rule, value, callback) => {
      var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
      if (re.test(value)) {
        callback();
      } else {
        callback(new Error("Email格式错误"));
      }
    };
    return {
      registerForm: {
        username: "",
        contact: "",
        address: "",
        phone: "",
        email: "",
        invited_code: "",
        password: "",
      },
      loginRules: {
        username: [
          {
            required: true,
            trigger: "blur",
            validator: validateUsername
          }
        ],
        password: [
          {
            required: true,
            trigger: "blur",
            validator: validatePassword
          }
        ],
        email: [
          {
            required: true,
            trigger: "blur",
            validator: validateEmail
          }
        ],
        contact: [
          {
            required: true,
            trigger: "blur"
          }
        ],
        phone: [
          {
            required: true,
            trigger: "blur",
            pattern:/^(1[34578]\d{9})$/
          }
        ],
        address: [
          {
            required: true,
            trigger: "blur"
          }
        ],
        invited_code: [
          {
            required: true,
            trigger: "blur"
          }
        ]
      },
      loading: false,
      passwordType: "password",
      redirect: undefined
    };
  },
  methods: {
    showPwd() {
      if (this.passwordType === "password") {
        this.passwordType = "";
      } else {
        this.passwordType = "password";
      }
      this.$nextTick(() => {
        this.$refs.password.focus();
      });
    },
    handleLogin() {
      this.$refs.registerForm.validate(valid => {
        if (valid) {
          this.loading = true;

          const payload = {
            confirm_email_base_url:
            window.location.href.split("/", 4).join("/") + "/unconfirmed/?token=",
            username: this.registerForm.username,
            email: this.registerForm.email,
            password: this.registerForm.password,
            contact: this.registerForm.contact,
            address: this.registerForm.address,
            phone: this.registerForm.phone,
            invited_code: this.registerForm.invited_code
          };
          postUsers(payload)
            .then(res => {
              console.log(res)
              if (res.msg == 'error'){
                console.log(res)
                  this.$message({
                message: res.infos,
                type: "error"
              });
              } else {
              this.$message({
                message: "确认邮件已发到您的邮箱" + this.registerForm.email,
                type: "success"
              });
              this.$router.push({
                path: "/login" || "/"
              });
              this.loading = false;
            }
            })
            .catch(() => {
              this.loading = false;
            });
        } else {
          console.log("error submit!!");
          return false;
        }
      });
    }
  }
};
</script>


<style lang="scss">
/* 修复input 背景不协调 和光标变色 */
/* Detail see https://github.com/PanJiaChen/vue-element-admin/pull/927 */

$bg: #283443;
$light_gray: #fff;
$cursor: #fff;

@supports (-webkit-mask: none) and (not (cater-color: $cursor)) {
  .login-container .el-input input {
    color: $cursor;
  }
}

/* reset element-ui css */
.login-container {
  .el-input {
    display: inline-block;
    height: 47px;
    width: 85%;

    input {
      background: transparent;
      border: 0px;
      -webkit-appearance: none;
      border-radius: 0px;
      padding: 12px 5px 12px 15px;
      color: $light_gray;
      height: 47px;
      caret-color: $cursor;

      &:-webkit-autofill {
        box-shadow: 0 0 0px 1000px $bg inset !important;
        -webkit-text-fill-color: $cursor !important;
      }
    }
  }

  .el-form-item {
    border: 1px solid rgba(255, 255, 255, 0.1);
    background: rgba(0, 0, 0, 0.1);
    border-radius: 5px;
    color: #454545;
  }
}
</style>

<style lang="scss" scoped>
$bg: #2d3a4b;
$dark_gray: #4f758a;
$light_gray: #eee;

.login-container {
  min-height: 100%;
  width: 100%;
  background-color: $bg;
  overflow: hidden;

  .login-form {
    position: relative;
    width: 520px;
    max-width: 100%;
    padding: 60px 35px 0;
    margin: 0 auto;
    overflow: hidden;
  }

  .tips {
    font-size: 14px;
    color: #fff;
    margin-bottom: 10px;

    span {
      &:first-of-type {
        margin-right: 16px;
      }
    }
  }

  .svg-container {
    padding: 6px 5px 6px 15px;
    color: $dark_gray;
    vertical-align: middle;
    width: 30px;
    display: inline-block;
  }

  .title-container {
    position: relative;

    .title {
      font-size: 26px;
      color: $light_gray;
      margin: 0px auto 40px auto;
      text-align: center;
      font-weight: bold;
    }
  }

  .show-pwd {
    position: absolute;
    right: 10px;
    top: 7px;
    font-size: 16px;
    color: $dark_gray;
    cursor: pointer;
    user-select: none;
  }
}
</style>
