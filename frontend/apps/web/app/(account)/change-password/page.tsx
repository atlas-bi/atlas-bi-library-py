import { changePasswordAction } from '@/actions/change-password-action'
import { ChangePaswordForm } from '@/components/forms/change-password-form'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Change password - Atlas'
}

export default function ChangePassword() {
  return <ChangePaswordForm onSubmitHandler={changePasswordAction} />
}
