function formatDetail(detail: unknown): string | null {
  if (typeof detail === 'string' && detail.trim()) {
    return detail
  };

  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => {
        if (typeof item === 'string') {
          return item
        }

        if (typeof item === 'object' && item !== null && 'msg' in item) {
          const message = item.msg
          return typeof message === 'string' ? message : ''
        }

        return ''
      })
      .filter(Boolean)

    if (messages.length > 0) {
      return messages.join('; ')
    };
  };

  return null;
};

export function getErrorMessage(error: unknown): string {
  if (typeof error === 'object' && error !== null) {
    const requestError = error as {
      data?: { detail?: unknown }
      message?: string
    };

    return (
      formatDetail(requestError.data?.detail)
      || requestError.message
      || 'Неизвестная ошибка'
    );
  };

  return 'Неизвестная ошибка';
};