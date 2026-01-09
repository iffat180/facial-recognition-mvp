// Utility to measure camera performance
export const measureCameraPerformance = (videoElement: HTMLVideoElement) => {
  if (!videoElement) return null;

  return {
    resolution: {
      width: videoElement.videoWidth,
      height: videoElement.videoHeight
    },
    readyState: videoElement.readyState,
    networkState: videoElement.networkState,
    currentTime: videoElement.currentTime,
    duration: videoElement.duration,
    paused: videoElement.paused,
    muted: videoElement.muted
  };
};

// Check if video is performing well
export const isVideoHealthy = (videoElement: HTMLVideoElement): boolean => {
  return (
    videoElement.readyState === 4 && // HAVE_ENOUGH_DATA
    !videoElement.paused &&
    videoElement.videoWidth > 0 &&
    videoElement.videoHeight > 0
  );
};
