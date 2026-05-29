# 代码边界规则

本文件定义 AI 在没有特定模块上下文时，编辑文件前的默认边界判断。

> **适用范围**：bug 修复、跨模块重构、单点改造等没有 `.ai/modules/<name>.md` 的场景。
> **覆盖规则**：单模块新功能 / 完整改造应在 `.ai/modules/<模块名>.md` 写更窄的 `## Code Boundary`，覆盖本文件默认。

## 边界分类

每个项目应在本文件中**具体填写**三档路径范围（glob，相对项目根）：

### Owned（可自由编辑）

通常包括：
- 业务页面 / 视图（如 `src/views/**`、`src/pages/**`）
- 按领域分组的 API、store、i18n（如 `src/api/modules/**`、`src/stores/modules/**`）
- AI 工作区（`.ai/**`）
- 项目文档（`docs/**`、根目录 `*.md`，但 `CLAUDE.md` / `AGENTS.md` 除外）

### Read-only references（可使用，不可直接改）

通常包括：
- 共享组件库（`src/components/**`）
- 共享 hooks / utils / directives（`src/hooks/**`、`src/utils/**`、`src/directives/**`）
- 布局、全局样式、全局配置（`src/layouts/**`、`src/styles/**`、`src/config/**`）
- 枚举、类型（`src/enums/**`、`src/types/**`、`src/typings/**`）
- 路由（`src/routers/**`）
- API 全局封装（如 `src/api/index.ts`、`src/api/config/**`）
- 应用入口与根组件（`src/main.ts`、`src/App.vue`）
- 静态资源（`src/assets/**`）
- 项目根的 `CLAUDE.md`、`AGENTS.md`、`.ai/rules/**`、`.claude/**`

改动此类文件需走下方的 **Shared Code Change Protocol**。

### Out-of-bounds（必须用户显式授权）

通常包括：
- 依赖与构建：`package.json`、`package-lock.json` / `pnpm-lock.yaml` / `yarn.lock`、`tsconfig.json`、`vite.config.*` / `webpack.config.*`、`postcss.config.*`
- 提交工具链：`commitlint.config.*`、`lint-staged.config.*`、`.husky/**`
- 环境变量：`.env`、`.env.*`
- IDE / CI：`.vscode/**`、`.idea/**`、`.github/**`、`.gitlab/**`
- 项目脚本与产物：`scripts/**`、`public/**`、`dist/**`、`build/**`、`node_modules/**`
- License、Changelog、API 文档快照等

## Shared Code Change Protocol（强制）

**适用范围：**
- 模块内被多处复用的公共组件 / 函数（如 `src/views/<module>/components/**` 被多页面引用、模块内复用的 `utils` / `hooks`）。
- 项目级共享代码（`src/components/**`、`src/hooks/**`、`src/utils/**`、`src/api/index.ts` 等）。

**强制要求：**
- 实际修改前，必须先向用户**告知影响范围**。
- 告知内容至少包含：
  1. 影响到哪些**模块**；
  2. 影响到哪些**功能点**；
  3. 是否涉及现有**调用方行为变化**。
- 未完成上述告知并得到用户**确认**前，不得开始修改公共代码。

**执行方式：**
- 无法明确影响范围时，先完成调用方排查（全局搜索引用）再提方案。
- 改动方案得到用户确认后才能实施。
- 作为通用 Code Change Protocol 的前置步骤执行。

## 模块级覆盖

需要为某模块写更紧的 boundary 时，在 `.ai/modules/<模块名>.md` 中添加 `## Code Boundary` 区块。该模块上下文存在时，模块级 boundary **优先于**本文件。

---

> **新项目部署**：删除上方「通常包括」的提示文字，填入项目实际路径 glob 后即可使用。
