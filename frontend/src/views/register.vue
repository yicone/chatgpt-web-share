<template>
  <div class="h-screen flex flex-col m-6">
    <div v-if="userStore.user" class="h-full mb-6 justify-center items-center">
      {{ $t('tips.jumpingPage') }}
    </div>
    <div v-else class="justify-center flex-1">
      <n-form ref="formRef" inline :label-width="0" :model="formValue" :rules="rules" :size="size" class="flex flex-wrap">
        <n-form-item path="user.username" class="w-full sm:w-auto">
          <n-input v-model:value="formValue.user.username" placeholder="用户名" :maxlength="20" />
        </n-form-item>
        <n-form-item path="user.email" class="w-full sm:w-auto">
          <n-auto-complete v-model:value="formValue.user.email" :options="autoCompleteOptions" placeholder="Email"
            :maxlength="50" />
        </n-form-item>
        <n-form-item path="user.password" class="w-full sm:w-auto">
          <n-input v-model:value="formValue.user.password" placeholder="密码" type="password" :maxlength="20" />
        </n-form-item>
        <n-form-item class="w-full sm:w-auto">
          <n-button attr-type="button" type="primary" @click="handleSignUpClick">
            创建账号
          </n-button>
        </n-form-item>
      </n-form>
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
import { Message } from '@/utils/tips';

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
    username: '',
    nickname: '',
    email: '',
    password: '',
  }
});
const size = ref<'small' | 'medium' | 'large'>('medium');
const rules = {
  user: {
    username: [
      {
        required: true,
        message: '请输入用户名',
        trigger: 'blur'
      },
      {
        pattern: /^(?=.{6,20}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$/,
        message: t("errors.badUsername"),
        trigger: 'blur'
      }
    ],
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

const handleSignUpClick = () => {
  formRef.value?.validate(async (errors) => {
    if (!errors) {
      formValue.value.user.nickname = formValue.value.user.username;
      await userStore.register(formValue.value.user as UserCreate)
      Message.success(t('tips.registerSuccess'));
      router.push({
        name: "login",
      }).then(() => {
        window.location.reload();
      })
    } else {
      console.log('error submit!!');
    }
  });
};



</script>