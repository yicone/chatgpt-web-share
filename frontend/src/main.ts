import Vue from "vue";
import pinia from "./store";
import { createApp } from "vue";
import "./style.css";
import App from "./App.vue";
import "uno.css";
import "@/api/interceptor";
import router from "./router";

import { i18n } from "./i18n";
import "highlight.js/styles/atom-one-dark.css";
import "highlight.js/lib/common";

import "katex/dist/katex.css";

// import * as Sentry from "@sentry/vue";
// import { BrowserTracing } from "@sentry/tracing";

const app = createApp(App);

// if (import.meta.env.VITE_DISABLE_SENTRY !== "yes") {
//   Sentry.init({
//     app,
//     dsn: "https://ac598690cd994673a8bd319b2c575213@o4504954233159680.ingest.sentry.io/4504954240827392",
//     integrations: [
//       new BrowserTracing({
//         routingInstrumentation: Sentry.vueRouterInstrumentation(router),
//         // tracePropagationTargets: ["localhost", "my-site-url.com", /^\//],
//       }),
//     ],
//     tracesSampleRate: 1.0,
//     ignoreErrors: ["AxiosError", "errors."]
//   });
// }

app.use(router);
app.use(pinia);
app.use(i18n);
// app.use(hljs.vuePlugin);

app.mount("#app");

declare global {
  interface Window {
    $message: any;
  }
}
