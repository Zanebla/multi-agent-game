import { RoleType } from '../types/message.types'

interface AvatarProps {
  role: RoleType
  className?: string
}

export default function Avatar({ role, className }: AvatarProps) {
  const getAvatarImage = () => {
    switch (role) {
      case 'USER':
        return '/images/user.jpg'
      case 'PM':
        return '/images/pm.jpg'
      case 'SDE':
        return '/images/sde.jpg'
      default:
        return '/images/default.jpg'
    }
  }

  return (
    <img
      src={getAvatarImage()}
      alt={`${role} avatar`}
      className={`${className} w-10 h-10 rounded-full object-cover`}
    />
  )
}
