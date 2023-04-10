<template>
  <div class="h-screen flex flex-col m-6">
    <div v-if="userStore.user" class="h-full mb-6 justify-center items-center">
      {{ $t('tips.jumpingPage') }}
    </div>
    <div v-else class="justify-center flex-1">
      <div>
        <n-h1 style="padding-top: 60px;font-family: Metropolis,sans-serif;font-size: 64px !important;">智享无界</n-h1>
        <p>网络不通畅？注册被拒？绑卡被拒？频繁的证明你是人类？😫</p>
        <p>Share GPT 为你提供快速，稳定，隐私安全，高性价比的 ChatGPT AI问答服务 🎉</p>
      </div>
      <n-button type="primary" class="mt-6 mb-6" @click="handleStartClick">开始使用</n-button>
      <p class="text-sm c-zinc-400">遇到问题，请联系客服💁 <n-a href="https://t.me/share_gpt" target="blank">ShareGPT官方合租群</n-a></p>
    </div>
    <div class="">
        
        <p>©2023 ShareGPT</p>
      </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useUserStore } from '@/store';
import { ref, computed } from 'vue';
import { FormInst } from 'naive-ui';
import { useI18n } from 'vue-i18n';
import { UserCreate } from "@/types/schema";
import UserProfileCard from '@/components/UserProfileCard.vue';

const router = useRouter();
const userStore = useUserStore();
const { t } = useI18n();

let target = "";
if (userStore.user) {
  target = "conversation";
  router.push({
    name: target,
  }).then(() => {
    window.location.reload();
  })
}

const formRef = ref<FormInst | null>(null);
const formValue = ref({
  user: {
    email: '',
    password: '',
  }
});
const size = ref<'small' | 'medium' | 'large'>('medium');
const rules = {
  user: {
    email: [
      {
        required: true,
        message: '请输入Email',
        trigger: 'blur'
      },
      {
        pattern: /^[^@\s]+@[^@\s]+\.[^@\s]+$/,
        message: t("errors.badEmail"),
        trigger: 'blur'
      }
    ],
    password: [
      {
        required: true,
        message: '请输入密码',
        trigger: 'blur'
      },
      {
        pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/,
        message: t("errors.badPassword"),
        trigger: 'blur'
      }
    ]
  }
};

const autoCompleteOptions = computed(() => {
  return ['@gmail.com', '@163.com', '@qq.com'].map((suffix) => {
    const prefix = formValue.value.user.email.split('@')[0]
    return {
      label: prefix + suffix,
      value: prefix + suffix
    }
  })
});

const handleStartClick = () => {
  router.push({
    name: "register",
  })
};



</script>