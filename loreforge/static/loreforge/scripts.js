document.querySelectorAll('.local-time').forEach((element) => {
  const utcTime = element.dataset.time;
  const localDate = new Date(utcTime);

  const formatted = localDate.toLocaleString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  });

  element.textContent = formatted;
});
