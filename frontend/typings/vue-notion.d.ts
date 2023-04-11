declare module 'vue-notion' {
  import { DefineComponent } from 'vue';

  export const NotionRenderer: DefineComponent;
  export function getPageBlocks(pageId: string): Promise<any>
}
