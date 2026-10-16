using UnityEngine;

public class Config : MonoBehaviour {
    [SerializeField]
    private int frameRate = 10;

    [SerializeField]
    private int vSyncCount = 0;

    // Start is called before the first frame update
    private void Start() {
        Application.targetFrameRate = frameRate;
        QualitySettings.vSyncCount = vSyncCount;
    }
}
