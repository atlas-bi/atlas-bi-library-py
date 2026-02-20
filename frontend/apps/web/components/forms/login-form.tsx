'use client'

import { loginFormSchema } from '@/lib/validation'
import { SubmitField } from '@frontend/ui/forms/submit-field'
import { TextField } from '@frontend/ui/forms/text-field'
import { ErrorMessage } from '@frontend/ui/messages/error-message'
import { zodResolver } from '@hookform/resolvers/zod'
import { signIn } from 'next-auth/react'
import { useSearchParams } from 'next/navigation'
import { useForm } from 'react-hook-form'
import type { z } from 'zod'

type LoginFormSchema = z.infer<typeof loginFormSchema>

export function LoginForm() {
  const search = useSearchParams()

  const { register, handleSubmit, formState } = useForm<LoginFormSchema>({
    resolver: zodResolver(loginFormSchema)
  })

  const onSubmitHandler = handleSubmit((data) => {
    signIn('credentials', {
      username: data.username,
      password: data.password,
      callbackUrl: '/'
    })
  })

  return (
    <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200 max-w-md w-full mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-2xl font-semibold tracking-tight text-gray-900 mb-2">
          Sign in to Atlas
        </h1>
        <p className="text-sm text-gray-600">
          Enter your credentials to access the library.
        </p>
      </div>

      {search.has('error') && search.get('error') === 'CredentialsSignin' && (
        <div className="mb-4">
          <ErrorMessage>Invalid username or password.</ErrorMessage>
        </div>
      )}

      <form
        method="post"
        action="/api/auth/callback/credentials"
        onSubmit={onSubmitHandler}
        className="space-y-6"
      >
        <div className="space-y-4">
          <TextField
            type="text"
            register={register('username')}
            formState={formState}
            label="Username"
            placeholder="Username or email"
          />

          <TextField
            type="password"
            register={register('password', { required: true })}
            formState={formState}
            label="Password"
            placeholder="••••••••"
          />
        </div>

        <button
          type="submit"
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 transition-colors"
        >
          Sign in
        </button>
      </form>
    </div>
  )
}
