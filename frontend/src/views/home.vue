<template>
  <div class="h-screen flex flex-col m-6">
    <div v-if="userStore.user" class="h-full mb-6 justify-center items-center">
      {{ $t('tips.jumpingPage') }}
    </div>
    <div v-else class="justify-center flex-1">
      <div>
        <n-space vertical size="large">
          <n-card class="custom-background">
            <!-- 在此处放置您的内容 -->
            <n-h1 style="padding-top: 60px;font-family: Metropolis,sans-serif;font-size: 64px !important;">{{
              $t("commons.siteSlogan") }}</n-h1>
          </n-card>
          <!-- 痛点部分 -->
          <n-card hoverable>
            <div class="card-content">
              <div class="section-title">想要访问 ChatGPT?</div>
              <ul class="custom-list">
                <li>无法或难以访问ChatGPT服务，网络速度非常慢。</li>
                <li>无法收到短信验证码，导致无法完成注册。</li>
                <li>订阅 Plus 需要绑定信用卡，但受限制国家的信用卡可能被拒绝。</li>
                <li>频繁遇到人机验证，影响使用体验。</li>
              </ul>
            </div>
          </n-card>
          <n-card :bordered="false" class="items-center mt-12">
            <h2>
              ShareGPT 为你提供
            </h2>
          </n-card>
          <n-grid cols="1 400:2 600:4" x-gap="12" :y-gap="8" item-responsive>
            <n-grid-item>
              <n-card hoverable title="开箱即用">
                <template #header-extra>
                </template>
                <div class="card-content">
                  <p>注册后立即开始使用。<br>免费账户每日有 10 次问答额度。</p>
                </div>
              </n-card>
            </n-grid-item>
            <n-grid-item>
              <n-card hoverable embedded title="流畅，稳定可靠">
                <template #header-extra>
                </template>
                <div class="card-content">
                  <p>采用优质链路连接。<br>Plus 模型更流畅稳定。</p>
                </div>
              </n-card>
            </n-grid-item>
            <n-grid-item>
              <n-card hoverable title="隐私安全">
                <template #header-extra>
                </template>
                <div class="card-content">
                  <p>与市场上的其他账号共享服务相比，你的聊天记录不会与他人分享。</p>
                </div>
              </n-card>
            </n-grid-item>
            <n-grid-item>
              <n-card hoverable embedded title="高性价比">
                <template #header-extra>
                </template>
                <div class="card-content">
                  <p>只需支付一小部分费用，即可使用 Plus 账号的付费模型，获得更智能、更快速的响应，并避免频繁的人机验证干扰。</p>
                </div>
              </n-card>
            </n-grid-item>
          </n-grid>
          <div class="mt-9 mb-9" style="text-align: center;">
            <n-button type="primary" size="large" class="center mt-6 mb-6" @click="handleStartClick">开始使用</n-button>
            <p class="text-sm c-zinc-400">遇到问题，请联系客服💁 <n-a href="https://t.me/share_gpt"
                target="blank">ShareGPT官方合租群</n-a>
            </p>
          </div>
        </n-space>
      </div>
    </div>
    <div class="mt-9 mb-9" style="text-align: center;">
      <p>© 2023 ShareGPT</p>
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