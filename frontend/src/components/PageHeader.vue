<template>
  <n-page-header>
    <template #title>
      <n-space :align="'center'">
        <div>
          <a href="/" style="text-decoration: none; color: inherit">{{ $t("commons.siteTitle") }}</a>
        </div>
        <div class="hidden sm:block">
          
        </div>
        <!-- <n-tag :bordered="false" type="success" size="small" class="hidden sm:inline-flex">
          {{ $t("commons.siteSlogan") }}
        </n-tag> -->
          <n-menu v-model:value="activeKey" mode="horizontal" :options="menuOptions" />
      </n-space>
    </template>
    <template #avatar>
      <n-avatar src="/chatgpt-icon.svg" />
    </template>
    <template #extra>
      <n-space>
        <div class="space-x-2">
          <div v-if="userStore.user" class="inline-block">
            <span class="hidden sm:inline mr-1">Hi, {{ userStore.user.nickname }}</span>
            <n-dropdown :options="getOptions()" placement="bottom-start">
              <n-button circle class="ml-2">
                <n-icon :component="SettingsSharp" />
              </n-button>
            </n-dropdown>
          </div>
          <div v-else class="text-gray-500 inline-block"><n-button v-if="!isLoginRoute" quaternary type="primary" @click="handleLoginClick">{{ $t("commons.login") }}</n-button></div>
          <n-button v-if="userStore.user?.is_superuser" circle @click="jumpToAdminOrConv">
            <n-icon :component="isInAdmin ? ChatFilled : ManageAccountsFilled" />
          </n-button>
          <n-button circle title="客服群" @click="openTelegram">
            <n-icon>
              <svg viewBox="0 0 32 32" width="1.2em" height="1.2em" data-v-c2914fc3=""><path fill="currentColor" d="m29.919 6.163l-4.225 19.925c-.319 1.406-1.15 1.756-2.331 1.094l-6.438-4.744l-3.106 2.988c-.344.344-.631.631-1.294.631l.463-6.556L24.919 8.72c.519-.462-.113-.719-.806-.256l-14.75 9.288l-6.35-1.988c-1.381-.431-1.406-1.381.288-2.044l24.837-9.569c1.15-.431 2.156.256 1.781 2.013z"></path></svg>
            </n-icon>
          </n-button>
          <n-button circle @click="toggleTheme">
            <n-icon :component="themeIcon" />
          </n-button>
          <n-dropdown :options="languageOptions" placement="bottom-start">
            <n-button circle>
              <n-icon :component="Language" />
            </n-button>
          </n-dropdown>
        </div>
      </n-space>
    </template>
  </n-page-header>
</template>

<script setup lang="ts">
import { useUserStore, useAppStore } from '@/store';
import { SettingsSharp, LogoGithub, Language } from '@vicons/ionicons5';
import { DarkModeRound, LightModeRound, ManageAccountsFilled, ChatFilled } from '@vicons/material';
import { useI18n } from 'vue-i18n';
import { Dialog, Message } from '@/utils/tips';
import router from '@/router';
import { useRoute } from 'vue-router';
import { DropdownOption, NIcon } from "naive-ui"
import type { MenuOption } from 'naive-ui'
import { ref, computed, h } from 'vue';
import UserProfileCard from './UserProfileCard.vue';
import { popupResetUserPasswordDialog } from '@/utils/renders';
import { resetUserPasswordApi } from '@/api/user';


const { t } = useI18n();
const userStore = useUserStore();
const appStore = useAppStore();
const route = useRoute();
const version = 'v' + import.meta.env.PACKAGE_VERSION;

console.log(route);

const menuOptions: MenuOption[] = [
  {
    label: () =>
      h(
        'a',
        {
          href: 'https://sharegpt.super.site/pricing',
          target: '_blank',
          rel: 'noopenner noreferrer'
        },
        '价格'
      ),
    key: 'pricing',
  },
  {
    label: () =>
      h(
        'a',
        {
          href: 'https://sharegpt.super.site/faq',
          target: '_blank',
          rel: 'noopenner noreferrer'
        },
        'FAQ'
      ),
    key: 'faq',
  },
]

const activeKey = ref<string | null>(null)

const isInAdmin = computed(() => {
  return route.path.startsWith('/admin');
})

const themeIcon = computed(() => {
  if (appStore.theme == 'dark') {
    return DarkModeRound
  } else {
    return LightModeRound
  }
})

const openTelegram = () => {
  window.open('https://t.me/share_gpt', '_blank');
}

const toggleTheme = () => {
  appStore.toggleTheme();
}

const languageOptions = [
  {
    label: '简体中文',
    key: 'zh-CN',
    props: {
      onClick: () => {
        appStore.setLanguage('zh-CN');
      }
    }
  },
  {
    label: 'English',
    key: 'en-US',
    props: {
      onClick: () => {
        appStore.setLanguage('en-US');
      }
    }
  }
]

const getOptions = (): Array<DropdownOption> => {
  const options: Array<DropdownOption> = [
    {
      label: t("commons.userProfile"),
      key: 'profile',
      props: {
        onClick: () => Dialog.info({
          title: t("commons.userProfile"),
          content: () => h(UserProfileCard, {}, {}),
          positiveText: t("commons.confirm"),
        })
      }
    },
    {
      label: t("commons.resetPassword"),
      key: 'resetpwd',
      props: {
        onClick: resetPassword
      }
    },
    {
      label: t("commons.logout"),
      key: 'logout',
      props: {
        onClick: () => Dialog.info({
          title: t("commons.logout"),
          content: t("tips.logoutConfirm"),
          positiveText: t("commons.confirm"),
          negativeText: t("commons.cancel"),
          onPositiveClick: async () => {
            await userStore.logout();
            console.warn('logout 1')
            Message.success(t('commons.logoutSuccess'));
            await router.push({ path: '/home' });
          }
        })
      }
    }
  ];
  return options;
}

const resetPassword = () => {
  popupResetUserPasswordDialog(
    async (password: string) => {
      await resetUserPasswordApi(userStore.user!.id, password);
    },
    () => { Message.info(t("tips.resetUserPasswordSuccess")) },
    () => { Message.error(t("tips.resetUserPasswordFailed")) }
  )
}

const jumpToAdminOrConv = async () => {
  if (isInAdmin.value) {
    await router.push({ name: 'conversation' });
  } else {
    await router.push({ name: 'admin' });
  }
}

const handleLoginClick = () => {
  router.push({ name: 'login' })
}


const isLoginRoute = computed(() => route.path === '/login')
</script>
