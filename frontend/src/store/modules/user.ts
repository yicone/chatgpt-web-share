import { getUserInfoApi, loginApi, LoginData, logoutApi, registerApi } from "@/api/user";
import { UserCreate, UserRead } from "@/types/schema";
import { clearCookie } from "@/utils/auth";
import { defineStore } from "pinia";
import { UserState } from "../types";

const useUserStore = defineStore("user", {
  state: (): UserState => ({
    user: null,
    savedUsername: null,
    savedPassword: null,
  }),
  getters: {
    userInfo(state: UserState): UserRead | null {
      return state.user;
    },
  },

  actions: {
    // Set user's information
    setInfo(user: UserRead) {
      this.$patch({ user });
    },

    setSavedLoginInfo(username: string, password: string) {
      this.$patch({ savedUsername: username, savedPassword: password });
    },

    // Reset user's information
    resetInfo() {
      this.$reset();
    },

    // Get user's information
    async fetchUserInfo() {
      const result = (await getUserInfoApi()).data;
      this.setInfo(result);
    },

    async register(userInfo: UserCreate) {
      await registerApi(userInfo);
    },

    // Login
    async login(loginForm: LoginData) {
      try {
        await loginApi(loginForm);
        // setToken(res.data.token);
      } catch (err) {
        clearCookie();
        throw err;
      }
    },

    // Logout
    async logout() {
      try {
        await logoutApi();
        console.warn('userStore.logout')
      } finally {
        this.resetInfo();
        clearCookie();
      }
    },
  },
});

export default useUserStore;
