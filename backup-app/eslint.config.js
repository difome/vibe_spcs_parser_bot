import js from '@eslint/js'
import globals from 'globals'
import vue from 'eslint-plugin-vue'
import vueTsConfig from '@vue/eslint-config-typescript'
import vuePrettierConfig from '@vue/eslint-config-prettier'
import tseslint from 'typescript-eslint'
import { defineConfig, globalIgnores } from 'eslint/config'

export default defineConfig([
  globalIgnores(['dist', 'node_modules']),
  js.configs.recommended,
  ...tseslint.configs.recommended,
  ...vue.configs['flat/essential'],
  vueTsConfig(),
  vuePrettierConfig(),
  {
    files: ['**/*.{ts,tsx,vue}'],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
    },
    rules: {
      'vue/multi-word-component-names': 'off',
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
    },
  },
])
