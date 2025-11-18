import { useLanguageStore } from '../stores/languageStore'
import { t as translate } from '../utils/translations'

export const useTranslation = () => {
  const { language } = useLanguageStore()
  
  const t = (key: string): string => {
    return translate(key, language)
  }
  
  return { t, language }
}
