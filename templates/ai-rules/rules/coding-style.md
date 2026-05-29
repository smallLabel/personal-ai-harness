# 编码风格规则

## 通用约定

- 项目通常配置 Prettier + ESLint + Stylelint，提交前由 lint-staged 自动执行。
- 具体配置以项目根目录的 `.prettierrc` / `.eslintrc` / `stylelint.config.*` 为准。
- 修改代码时遵守项目现有缩进、引号、行宽等设置，**不要自作主张改风格**。

## Vue 组件

- 使用 `<script setup lang="ts">` 语法。
- 组件名通过 `defineOptions({ name: "ComponentName" })` 定义，或写在 `<script>` 标签的 `name` 上。
- 模板中组件标签可使用 kebab-case 或 PascalCase，遵循项目现有写法。
- 优先使用 Composition API；除非项目历史代码全部 Options API，否则不混用。

## TypeScript

- 启用严格模式（`strict: true`）。
- 不强制显式函数返回类型（让 TS 推断）。
- 必要时可用 `any`，但应优先精确类型；导出的公共 API 不要 `any`。
- 禁止 `@ts-ignore`，需要忽略时用 `@ts-expect-error`（强制写明理由且失效时报错）。
- 使用 `let` / `const`，禁用 `var`。

## 禁止事项

- 不允许多个连续空行（最多 1 行空行）。
- 避免不安全的 `as` 类型断言；用类型守卫或先校验。
- 不直接修改 props，需要可变状态用 `computed` 或本地 `ref`。
- 不在生产代码留 `console.log` / `debugger`。

## 路径别名

按项目 `tsconfig.json` 和构建配置的别名使用（常见为 `@` 代表 `src/`）：

```typescript
import { Foo } from "@/components/Foo";
import { getListApi } from "@/api/modules/system";
```

## 注释

- 默认**不写注释**——好的命名比注释更有价值。
- 仅在 WHY 不明显时写一行简短注释（隐式约束、坑、补偿历史 bug 等）。
- 不写 WHAT（代码本身已经说明）。
- 不引用当前任务 / PR / issue 编号（这些会随时间腐烂，应放在 commit / PR 描述里）。

> 若项目专门要求「新代码加简短注释」等，以项目入口（`CLAUDE.md` / `AGENTS.md`）的约定为准。
