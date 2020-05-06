using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.EventSystems;
using TMPro;

[ExecuteAlways]
public class BlobController : MonoBehaviour, IDragHandler
{
    public bool panWithForce;

    public Color color;
    public float size = 1f, blobNoise = 2f;
    [Range(0f, 0.8f)]
    public float blobAmplitude = 0.3f;
    int maxColliders = 4;

    List<BlobController> colliders = new List<BlobController>();
    [HideInInspector]
    public Rigidbody2D rigidBody2D;
    SpriteRenderer sprite;
    Material tempMaterial;
    TMP_Text text;

    BlobAreaController blobArea;

    private void Start()
    {
        rigidBody2D = GetComponent<Rigidbody2D>();
        sprite = GetComponent<SpriteRenderer>();
        text = GetComponentInChildren<TMP_Text>();
        blobArea = GetComponentInParent<BlobAreaController>();

        CreateAndAssignMaterial();
        UpdateBlobProperties();
    }

    void CreateAndAssignMaterial()
    {
        tempMaterial = new Material(Shader.Find("Shader Graphs/Blob Shader 2D"));
        tempMaterial.SetVector("_Color", color);
        sprite.material = tempMaterial;
    }

    void UpdateBlobProperties()
    {
        tempMaterial.SetFloat("_OwnSize", size);
        tempMaterial.SetFloat("_BlobAmplitude", blobAmplitude);
        tempMaterial.SetFloat("_BlobNoise", blobNoise);
    }

    void Update()
    {
        if (!tempMaterial)
            CreateAndAssignMaterial();

        tempMaterial.SetVector("_SelfPos", transform.position);

        colliders = new List<BlobController>();
        foreach (var item in Physics2D.OverlapCircleAll(transform.position, 8f))
        {
            if (item.gameObject != gameObject)
            {
                colliders.Add(item.GetComponent<BlobController>());
            }
        }

        for (int i = 0; i < colliders.Count; i++)
        {
            Vector4 input = colliders[i].transform.position;
            input.w = colliders[i].size * Mathf.Pow(colliders[i].transform.localScale.x, 2);
            tempMaterial.SetVector($"Collider{i + 1}", input);
        }

        for (int i = colliders.Count; i <= maxColliders; i++)
        {
            tempMaterial.SetVector($"Collider{i + 1}", new Vector4());
        }
    }

    public void OnDrag(PointerEventData eventData)
    {
        if (panWithForce)
        {
            rigidBody2D.AddForce(eventData.delta / Screen.width * 15000f);
            blobArea.PanBlobs(eventData.delta / 4f);
        }
        else
        {
            rigidBody2D.MovePosition(eventData.pointerCurrentRaycast.worldPosition);
            blobArea.PanBlobs(eventData.delta / 2f);
        }
    }
}
