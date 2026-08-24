import js from '@eslint/js'
import globals from 'globals'
import react from 'eslint-plugin-react'
import reactHooks from 'eslint-plugin-react-hooks'

export default [
  {
    ignores: ['dist/**', 'node_modules/**'],
  },
  {
    files: ['src/**/*.{js,jsx}'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: globals.browser,
      parserOptions: { ecmaFeatures: { jsx: true } },
    },
    plugins: {
      react,
      'react-hooks': reactHooks,
    },
    rules: {
      ...js.configs.recommended.rules,
      ...reactHooks.configs.recommended.rules,
      'react/jsx-uses-vars': 'error',
      'no-unused-vars': ['error', { varsIgnorePattern: '^React$' }],
    },
  },
  {
    files: ['src/features/**/*.{js,jsx}'],
    rules: {
      'no-restricted-imports': [
        'error',
        {
          patterns: [
            {
              group: ['@/pages/**', '@/routes/**', '@/layouts/**', '@/features/**'],
              message: 'Feature 只能依赖共享层；Feature 内部请使用相对路径，禁止跨 Feature 引用。',
            },
          ],
        },
      ],
    },
  },
  {
    files: [
      'src/api/**/*.{js,jsx}',
      'src/components/**/*.{js,jsx}',
      'src/contexts/**/*.{js,jsx}',
      'src/hooks/**/*.{js,jsx}',
      'src/lib/**/*.{js,jsx}',
      'src/utils/**/*.{js,jsx}',
    ],
    rules: {
      'no-restricted-imports': [
        'error',
        {
          patterns: [
            {
              group: ['@/features/**', '@/pages/**', '@/routes/**'],
              message: '共享层不能反向依赖 Feature、页面或路由层。',
            },
          ],
        },
      ],
    },
  },
]
