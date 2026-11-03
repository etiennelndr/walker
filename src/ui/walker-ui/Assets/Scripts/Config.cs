using UnityEngine;

public class Config : MonoBehaviour {
    [SerializeField]
    [Tooltip("Target number of frames per second")]
    private int frameRate = 10;

    [SerializeField]
    [Tooltip("Screen refreshes between two frames, or 0 to disable vertical sync")]
    private int vSyncCount;

    // Start is called before the first frame update
    private void Start() {
        Application.targetFrameRate = frameRate;
        QualitySettings.vSyncCount = vSyncCount;
    }
}
